# Reference — iOS (Xcode / clang / ld / CocoaPods / signing)

Chỉ load file này khi build chết ở **Stage 7–8 trên iOS**. Lỗi C#, IL2CPP, Burst, linker của Unity
nằm ở `unity-common.md`.

Khác Android ở một điểm quan trọng: Unity **chỉ export project Xcode**. Rất nhiều lỗi ở đây xảy ra
*sau khi Unity đã báo build thành công* — chúng nằm trong log `xcodebuild`, không nằm trong `Editor.log`.
Nếu user đưa `Editor.log` mà log kết thúc bằng "Build completed with a result of 'Succeeded'", hỏi họ
log `xcodebuild` chứ đừng cố tìm lỗi trong `Editor.log`.

Thứ tự đọc iOS: `The following build commands failed:` (danh sách task chết, ở cuối) → quay ngược lên
tìm dòng `error:` **đầu tiên bên trong task đó**. Dòng `** BUILD FAILED **` chỉ là tổng kết.

## Mục lục

- [Cụm pattern cho lượt count đầu tiên](#cụm-pattern-cho-lượt-count-đầu-tiên)
- [1. Xcode 15/16 — bẫy phiên bản](#1-xcode-1516--bẫy-phiên-bản)
- [2. Trùng file / trùng symbol](#2-trùng-file--trùng-symbol)
- [3. Linker (ld)](#3-linker-ld)
- [4. Compile: clang / Swift / bridging](#4-compile-clang--swift--bridging)
- [5. Script phase & Unity post-process](#5-script-phase--unity-post-process)
- [6. Signing / provisioning](#6-signing--provisioning)
- [7. CocoaPods](#7-cocoapods)
- [8. Toolchain & môi trường máy](#8-toolchain--môi-trường-máy)
- [Xác định `error:` nào là gốc](#xác-định-error-nào-là-gốc)

---

## Cụm pattern cho lượt count đầu tiên

```
Sandbox: rsync.* deny|libarclite|Multiple commands produce|duplicate symbol|Undefined symbols for architecture|library not found for|framework not found|Command PhaseScriptExecution failed|no such module|Swift Compiler Error|bitcode is not supported|requires a development team|doesn't include signing certificate|No profiles for|CocoaPods could not find compatible versions|xcrun: error:|clang: error:|The following build commands failed
```

---

## 1. Xcode 15/16 — bẫy phiên bản

Hai lỗi đầu bảng này chiếm phần lớn ca "hôm qua build được, hôm nay update Xcode xong chết".

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Sandbox: rsync\(\d+\) deny.*file-write-create` | PROJECT CONFIG | Xcode 15 bật `ENABLE_USER_SCRIPT_SANDBOXING=YES`; script phase của Unity/CocoaPods ghi file nên bị chặn | Build Settings → **User Script Sandboxing = No**. Tự động hoá bằng PostProcessBuild: `SetBuildProperty(target, "ENABLE_USER_SCRIPT_SANDBOXING", "NO")` |
| `SDK does not contain 'libarclite' at the path` | PROJECT CONFIG | Xcode 15 bỏ `libarclite`; pod/plugin còn để deployment target < 11 | Nâng deployment target của pod đó ≥ 12 trong `Podfile` (`post_install` loop), hoặc nâng **Target minimum iOS Version** trong PlayerSettings |
| `bitcode is not supported` · `-fembed-bitcode is not supported` | PROJECT CONFIG | Xcode 14+ bỏ bitcode nhưng plugin/PlayerSettings vẫn bật | Player Settings → tắt bitcode; hoặc `SetBuildProperty(target, "ENABLE_BITCODE", "NO")` |
| `was built for newer .* version .* than being linked` | 3RD-PARTY | Framework build cho iOS mới hơn deployment target | Nâng deployment target, hoặc xin bản framework build lại |
| `building for iOS Simulator, but linking .* built for iOS` · `was built for` + `simulator` | 3RD-PARTY | Framework chỉ có slice device, đang build simulator (hoặc ngược lại) | Build lên device thật; hoặc dùng `.xcframework` có đủ slice; hoặc `EXCLUDED_ARCHS[sdk=iphonesimulator*] = arm64` |

## 2. Trùng file / trùng symbol

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Multiple commands produce '.*'` | 3RD-PARTY | Cùng một file bị add hai lần vào **Copy Bundle Resources** — hay gặp khi một SDK vừa nằm trong `Assets/Plugins/iOS/` vừa được CocoaPods kéo về | Xoá bản trùng: hoặc bỏ file trong `Assets/Plugins/iOS/`, hoặc bỏ pod. Log nêu rõ target + tên file |
| `duplicate symbol '_?(\w+)' in:` | 3RD-PARTY | Hai SDK cùng nhúng một static lib (`libz`, `libGoogleUtilities`, adapter quảng cáo…) | Hai dòng ngay dưới nêu 2 file `.o` — từ đó suy ra 2 SDK. Bỏ một bản; nếu cả hai đều cần thì xin bản dynamic framework |
| `duplicate symbol .* in: .*libiPhone-lib\.a` | 3RD-PARTY | Plugin nhúng lại symbol Unity đã có | Bỏ lib thừa trong `Assets/Plugins/iOS/` |
| `Build input file cannot be found` | PROJECT CONFIG | Post-process script tham chiếu file không tồn tại (hoặc bị `.gitignore`) | Kiểm tra script trong `Assets/Editor/`; check file có được commit không |

## 3. Linker (ld)

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Undefined symbols for architecture arm64` | PROJECT CONFIG | Thiếu framework hệ thống, hoặc thiếu cờ `-ObjC` khiến category Obj-C không được nạp | Dòng `"_XXX", referenced from:` ngay dưới cho biết symbol nào. Tên bắt đầu bằng `_OBJC_CLASS_$_` → thiếu framework/lib chứa class đó. Thêm framework trong PostProcessBuild bằng `AddFrameworkToProject` |
| `library not found for -l(\w+)` | PROJECT CONFIG | Khai `-lXxx` trong Other Linker Flags nhưng lib không có trong project | Bỏ cờ thừa, hoặc add lib. Thường do plugin bị xoá mà cờ còn sót trong `Podfile`/post-process |
| `framework not found (\w+)` | PROJECT CONFIG | Tương tự với framework | Add lại framework, kiểm tra `FRAMEWORK_SEARCH_PATHS` |
| `ld: symbol\(s\) not found for architecture` | PROJECT CONFIG | Dòng tổng kết của ld — 🟡 CASCADE, không phải root cause | Root cause là các dòng `Undefined symbols` phía trên |
| `Ignoring file .* file was built for archive which is not the architecture being linked` | 3RD-PARTY | Lib thiếu slice arm64 (lib cũ chỉ có armv7) | Xin bản mới; lib chỉ hỗ trợ armv7 thì không dùng được nữa |

## 4. Compile: clang / Swift / bridging

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `no such module '(\w+)'` | 3RD-PARTY | Import Swift module chưa được build/chưa có pod, hoặc mở `.xcodeproj` thay vì `.xcworkspace` | Mở đúng `Unity-iPhone.xcworkspace` khi có CocoaPods; chạy lại `pod install` |
| `Swift Compiler Error` · `error: cannot find '(\w+)' in scope` | 3RD-PARTY | Swift version lệch với code plugin | Đặt `SWIFT_VERSION` cho khớp (thường 5.0) qua PostProcessBuild |
| `bridging header .* does not exist` · `failed to import bridging header` | PROJECT CONFIG | Đường dẫn bridging header sai sau khi Unity re-export | Set `SWIFT_OBJC_BRIDGING_HEADER` trong PostProcessBuild, không sửa tay trong Xcode (mất khi export lại) |
| `clang: error: linker command failed with exit code 1` | PROJECT CONFIG | Dòng tổng kết của clang — 🟡 CASCADE | Nguyên nhân nằm ở các dòng `ld:` / `duplicate symbol` phía trên |
| `'(\w+\.h)' file not found` | 3RD-PARTY | Header search path sai, hoặc plugin thiếu file | Kiểm tra `HEADER_SEARCH_PATHS`; xác nhận plugin import đủ file |
| `Use of undeclared identifier` trong file `Assets/Plugins/iOS/*` | PROJECT CODE | Code Obj-C do team viết bị lỗi | Đây là **code nhà mình** — được đọc file và phân tích sâu |

## 5. Script phase & Unity post-process

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Command PhaseScriptExecution failed with a nonzero exit code` | PROJECT CODE | Một Run Script phase chết. Rất hay là script do team/plugin thêm | Cuộn lên tìm dòng `PhaseScriptExecution` gần nhất để biết **script nào**; stdout của nó in ngay trên dòng failed |
| `\[!\] .* error: /bin/sh` · `Permission denied` | ENVIRONMENT | Script không có quyền chạy | `chmod +x` file script |
| `BuildFailedException` trong `OnPostprocessBuild` | PROJECT CODE | Editor script của project ném exception khi hậu xử lý Xcode project | **Ưu tiên số 1** — đọc file Editor script tương ứng và phân tích sâu |
| `Cannot read PBXProject` · `key .* not found` | PROJECT CODE | Post-process script dùng GUID target sai (Unity 2019.3 đổi sang 2 target: UnityFramework + Unity-iPhone) | Dùng `GetUnityFrameworkTargetGuid()` / `GetUnityMainTargetGuid()` đúng chỗ |

## 6. Signing / provisioning

Nhóm này gần như luôn là PROJECT CONFIG hoặc tài khoản, **không bao giờ là lỗi code**.

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `requires a development team. Select a development team in the Signing & Capabilities editor` | PROJECT CONFIG | Chưa set Team ID | Player Settings → **Signing Team ID**, hoặc set trong Xcode |
| `doesn't include signing certificate` · `No signing certificate .* found` | PROJECT CONFIG | Máy chưa có cert tương ứng | Cài cert vào Keychain; hoặc dùng Automatic signing |
| `No profiles for '.*' were found` | PROJECT CONFIG | Bundle ID không khớp profile nào | Sửa bundle ID cho khớp, hoặc tạo profile mới trên Apple Developer |
| `Provisioning profile .* doesn't include the .* entitlement` | PROJECT CONFIG | Bật capability (Push, IAP, Sign in with Apple) nhưng profile chưa có | Bật capability trên portal rồi regenerate profile |
| `Command CodeSign failed` | PROJECT CONFIG | Tổng kết — đọc dòng trên để biết cert hay entitlement | |

## 7. CocoaPods

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `\[!\] CocoaPods could not find compatible versions for pod` | 3RD-PARTY | Hai SDK yêu cầu hai khoảng version xung khắc của cùng một pod | Log liệt kê ràng buộc của từng bên. Nâng SDK cũ hơn, hoặc ghim version trung gian thoả cả hai |
| `The .* target has .* deployment target .* but the .* pod requires` | 3RD-PARTY | Deployment target project thấp hơn pod yêu cầu | Nâng iOS target trong PlayerSettings |
| `\[!\] No podspec found for` · `Unable to find a specification for` | ENVIRONMENT | Repo pod chưa cập nhật | `pod repo update` rồi `pod install` |
| `pod install` + `not found` / `command not found` | ENVIRONMENT | Chưa cài CocoaPods trên máy build | `sudo gem install cocoapods`; trên CI phải thêm bước cài |

## 8. Toolchain & môi trường máy

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `xcrun: error: unable to find utility` · `xcode-select: error:` | ENVIRONMENT | Command Line Tools chưa chọn đúng Xcode | `sudo xcode-select -s /Applications/Xcode.app` |
| `Unable to find a destination matching the provided destination specifier` | ENVIRONMENT | Sai tham số `-destination` của `xcodebuild` (hay gặp trên CI) | Sửa lệnh CI, dùng `generic/platform=iOS` khi archive |
| `The operation couldn't be completed. No space left on device` | ENVIRONMENT | Hết đĩa (DerivedData ăn rất nhiều) | Xoá `~/Library/Developer/Xcode/DerivedData` |
| `Command Ld emitted errors but did not return a nonzero exit code` | ENVIRONMENT | Bug Xcode / hết RAM giữa chừng | Clean build folder, build lại |

---

## Xác định `error:` nào là gốc

Log `xcodebuild` in **song song nhiều target**, nên các dòng `error:` không theo thứ tự nhân quả. Cách
làm đúng:

1. Xuống cuối tìm khối:
   ```
   The following build commands failed:
       CompileC .../AppLovinMAX.o ...
       Ld .../UnityFramework normal
   (2 failures)
   ```
   Khối này cho biết **command nào** chết.
2. Quay ngược lên grep tên command đó (`CompileC .../AppLovinMAX.o`), lấy `-C 8`.
3. Dòng `error:` **đầu tiên trong khối command đó** là root cause. Các dòng `clang: error: linker command
   failed` và `** BUILD FAILED **` luôn là 🟡 CASCADE.

Nếu có cả `CompileC` lẫn `Ld` fail, ưu tiên `CompileC` — không compile được thì đương nhiên không link
được, nhưng ngược lại thì không.
