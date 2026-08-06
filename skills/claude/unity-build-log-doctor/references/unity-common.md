# Reference — Unity chung (C# / asset / build callback / IL2CPP / Burst / linker)

Load file này cho **Stage 1–6**, tức mọi thứ xảy ra *trước khi* Unity giao việc cho Gradle/Xcode. Nếu
log đã chạy tới `> Task :` hay `xcodebuild` thì phần lớn nội dung ở đây không còn liên quan — sang
`android.md` / `ios.md`.

Đặc điểm chung của Stage 1–6: lỗi **nằm trong code hoặc cấu hình của chính project**, nên tỉ lệ đào sâu
có ích cao hơn hẳn Stage 7–8 (vốn phần nhiều là xung đột SDK bên thứ ba).

## Mục lục

- [Cụm pattern cho lượt count đầu tiên](#cụm-pattern-cho-lượt-count-đầu-tiên)
- [1. Compile C#](#1-compile-c)
- [2. Assembly / asmdef](#2-assembly--asmdef)
- [3. Build callback của project — ưu tiên số 1](#3-build-callback-của-project--ưu-tiên-số-1)
- [4. Scene & PlayerSettings](#4-scene--playersettings)
- [5. Shader & asset import](#5-shader--asset-import)
- [6. IL2CPP](#6-il2cpp)
- [7. Burst](#7-burst)
- [8. UnityLinker / managed stripping](#8-unitylinker--managed-stripping)
- [9. Addressables / Scriptable Build Pipeline](#9-addressables--scriptable-build-pipeline)
- [10. Môi trường & license](#10-môi-trường--license)
- [Warning nào đáng lo (dùng cho Mode 2)](#warning-nào-đáng-lo-dùng-cho-mode-2)

---

## Cụm pattern cho lượt count đầu tiên

```
error CS\d+|Compilation failed|will not be loaded due to errors|Multiple precompiled assemblies|Unable to resolve reference|Shader error in|BuildFailedException|IPreprocessBuildWithReport|OnPostprocessBuild|IL2CPP error|il2cpp\.exe.*exited|Burst error BC\d+|UnityLinker|Managed Stripping|SBP Error|No valid Unity Editor license|not enough space on the disk
```

---

## 1. Compile C#

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `error CS0246: The type or namespace name '(\w+)' could not be found` | PROJECT CODE | Thiếu `using`, thiếu reference asmdef, hoặc class vừa bị xoá/đổi tên | Nếu tên type thuộc package → thiếu reference trong asmdef. Đây là lỗi C# hay bị **cascade** nhất: một class hỏng kéo theo hàng chục CS0246 ở file khác — root cause là lỗi đầu tiên theo thứ tự compile |
| `error CS0246: .* 'UnityEditor'` · `The type or namespace name 'UnityEditor' could not be found` | PROJECT CODE | Code Editor lọt vào build player: file nằm ngoài folder `Editor/`, hoặc thiếu `#if UNITY_EDITOR` | Chuyển file vào `Editor/`, hoặc bọc `#if UNITY_EDITOR ... #endif`. Đây là lỗi **chỉ xuất hiện khi build**, không thấy trong Editor → dev hay bối rối |
| `error CS0103: The name '(\w+)' does not exist in the current context` | PROJECT CODE | Symbol chỉ tồn tại dưới một define nào đó (`UNITY_ANDROID`, `UNITY_EDITOR`, define của SDK) | Kiểm tra Scripting Define Symbols của **platform đang build**, không phải platform đang mở |
| `error CS0227: Unsafe code may only appear if compiling with /unsafe` | PROJECT CONFIG | Dùng `unsafe` mà asmdef chưa bật | Tick **Allow 'unsafe' Code** trong asmdef (hoặc PlayerSettings nếu code ở Assembly-CSharp) |
| `error CS8107` · `Feature '.*' is not available in C# (\d+)` | PROJECT CONFIG | Cú pháp C# mới hơn bản Unity hỗ trợ | Viết lại theo C# version Unity dùng (Unity 2021 → C# 9, Unity 6 → C# 9/10 tuỳ bản) |
| `error CS0234: The type or namespace name '(\w+)' does not exist in the namespace` | PROJECT CODE | Thiếu assembly reference (hay gặp `UnityEngine.UI`, `TMPro`, `Newtonsoft`) | Thêm reference vào asmdef |
| `error CS1061: .* does not contain a definition for` | PROJECT CODE | Gọi API đã đổi/xoá sau khi update package. Bản **instance member** | Xem changelog package, sửa call site |
| `error CS0117: '(\w+)' does not contain a definition for '(\w+)'` | PROJECT CODE | Bản **static/type member** của CS1061. Rất hay chỉ là **sai hoa/thường** (`User.data` vs `User.Data`) sau một đợt refactor đổi tên | Tra khai báo thật + một call site anh em để lấy đúng tên. Xem "Tra tên đúng" bên dưới |
| `Compilation failed: (\d+) error\(s\)` | — | Dòng tổng kết, dùng để đếm — 🟡 CASCADE | Số này giúp biết còn bao nhiêu lỗi chưa in ra |

**Quy tắc gộp:** hàng chục `CS0246` cùng trỏ về **một type** = một lỗi, gộp lại `x12`. Nhiều type khác
nhau = nhiều lỗi thật, nhưng vẫn kiểm tra xem chúng có cùng đến từ một assembly hỏng không.

**Tra tên đúng.** Với `CS0117` / `CS1061` / `CS0246` / `CS0103`, đọc ±15 dòng quanh chỗ lỗi chỉ cho
biết *cái tên đang dùng là sai* — không cho biết *tên đúng là gì*, mà đó mới là thứ dev cần. Bỏ ra
đúng một lượt Grep tìm khai báo thật (`public static .*<Tên>`) hoặc một call site anh em dùng cùng
symbol. Kết quả biến "member `data` không tồn tại" thành "phải là `Data`, chữ D hoa" — chênh nhau rất
xa về mức hữu ích.

### Vì sao Editor chạy ngon mà build lại chết

Đây là câu hỏi thật sự trong đầu dev khi CI fail còn máy họ thì không, kể cả khi họ không hỏi thành
lời. Gần như luôn là do **code được compile ở build nhưng không được compile trong Editor**:

| Tình huống | Dấu hiệu | Vì sao Editor không thấy |
|---|---|---|
| Code nằm trong nhánh `#else` của `#if UNITY_EDITOR` | Dòng lỗi nằm giữa `#else` và `#endif` | Editor chỉ compile nhánh `#if`; nhánh `#else` **chưa bao giờ được compile** cho tới khi build player. Lỗi nằm im ở đó bao lâu cũng được |
| Code trong `#if !UNITY_EDITOR`, `#if UNITY_ANDROID`, `#if UNITY_IOS`, define của SDK | Lỗi chỉ xuất hiện ở một platform | Define active của Editor khác define của platform đích |
| Ngược lại: dùng `UnityEditor` ngoài folder `Editor/` | `CS0246 ... 'UnityEditor'` | Editor có assembly đó, player build thì không |

Hệ quả đáng chú ý: lỗi kiểu này **fail giống hệt nhau trên mọi platform**. Nếu user nói "Android fail,
iOS *cũng* fail", rất nên kiểm tra xem có phải **cùng một lỗi** không, thay vì chẩn đoán hai lần. Trong
báo cáo hãy nói thẳng điều đó — nó biến hai vé bug thành một.

## 2. Assembly / asmdef

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Assembly .* will not be loaded due to errors` | PROJECT CODE | Assembly khác compile fail → assembly này không nạp được | 🟡 CASCADE. Tìm assembly hỏng gốc |
| `Multiple precompiled assemblies with the same name` | 3RD-PARTY | Cùng một DLL nằm ở hai chỗ (hay gặp `Newtonsoft.Json.dll`) | Xoá một bản; nếu do package kéo về thì loại DLL trong `Assets/Plugins/` |
| `Unable to resolve reference '(\w+)'` | PROJECT CONFIG | asmdef trỏ tới assembly không tồn tại / bị đổi tên | Sửa danh sách references trong asmdef |
| `Assembly with name .* already exists` | PROJECT CONFIG | Hai asmdef trùng tên | Đổi tên một cái |
| `Cyclic assembly references detected` | PROJECT CONFIG | A tham chiếu B, B tham chiếu A | Tách phần dùng chung ra assembly thứ ba |
| `.* is not allowed to reference .*` (Define Constraints) | PROJECT CONFIG | asmdef bị chặn bởi define constraint hoặc platform filter | Sửa Define Constraints / Platforms trong asmdef |

## 3. Build callback của project — ưu tiên số 1

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `BuildFailedException` | PROJECT CODE | Code Editor của team chủ động ném ra để chặn build (hoặc lỗi thật trong callback) | Đọc message + stack. Nếu stack có namespace của project → chắc chắn code nhà mình |
| `IPreprocessBuildWithReport` · `IPostprocessBuildWithReport` · `OnPreprocessBuild` · `OnPostprocessBuild` trong stack | PROJECT CODE | Callback ném `NullReferenceException` / `FileNotFoundException` / `DirectoryNotFoundException` | Đọc Editor script tương ứng, ±15 dòng quanh dòng log chỉ ra |
| `UnityEditor.BuildPlayerWindow\+BuildMethodException` | PROJECT CODE | Wrapper của Unity quanh exception thật | 🟡 CASCADE — nguyên nhân là exception **bên trong**, thường in ngay phía trên |
| `NullReferenceException` + stack có `Assets/.*Editor.*\.cs:\d+` | PROJECT CODE | Callback đọc asset/`EditorPrefs`/path không tồn tại trên máy này hoặc trên CI | Sửa callback cho chịu được trường hợp thiếu |

**Vì sao nhóm này luôn là BLOCKER:** stacktrace đi qua `UnityEditor.BuildPipeline.BuildPlayerInternal`
nên **trông y hệt lỗi engine**, dev hay bỏ qua và đi tìm lỗi ở chỗ khác. Cứ thấy một frame trỏ vào
`Assets/**/Editor/**.cs` là biết code do team viết. Đây là ca đáng đào sâu nhất trong toàn bộ skill.

## 4. Scene & PlayerSettings

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Scene '.*' \(.*\) couldn't be loaded because it has not been added to the build settings` | PROJECT CONFIG | Scene bị bỏ tick / bị xoá khỏi Build Settings | Thêm lại scene vào Build Settings |
| `No scenes are added to the build` · `Build contains 0 scenes` | PROJECT CONFIG | Build Settings rỗng | Thêm scene |
| `Missing Project ID` · `Bundle Identifier has not been set up correctly` | PROJECT CONFIG | Bundle ID còn để mặc định `com.Company.ProductName` | Đặt bundle ID thật trong PlayerSettings |
| `Requested build target group .* doesn't match active build target` | PROJECT CONFIG | Script build gọi sai target group | Sửa script build; hoặc switch platform trước |

## 5. Shader & asset import

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Shader error in '(.*)': (.*) at line (\d+)` | PROJECT CODE / 3RD-PARTY | Shader sai cú pháp, hoặc dùng feature không có trên target (`#pragma target` quá cao) | Shader trong `Assets/_Project/` → code nhà mình, đào sâu. Shader trong package → thường do target/API graphics |
| `Shader error in .* undeclared identifier` | PROJECT CODE | Include thiếu hoặc keyword không được define ở variant đang compile | Kiểm tra `#include` và `#pragma multi_compile` |
| `Compute shader .* has no kernel` · `Kernel .* not found` | PROJECT CODE | Compute shader không compile được trên platform đích | Kiểm tra `#pragma kernel` và graphics API |
| `AssetImportWorker.* Error` · `Import Error` | PROJECT CONFIG | Asset hỏng / import setting không hợp lệ | Reimport asset đó; kiểm tra file có bị hỏng khi merge |
| `Failed to compile shader variants` · `Shader compiler: Compile .* failed` | PROJECT CONFIG | Máy build thiếu shader compiler hoặc thiếu RAM khi build variant lớn | Xem thêm log `Logs/shadercompiler-*.log` |
| `MissingReferenceException` / `The referenced script .* is missing` khi build | PROJECT CODE | Prefab/scene trỏ tới script đã xoá | Sửa prefab/scene; thường xuất hiện sau khi xoá class |

## 6. IL2CPP

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `IL2CPP error for method '(.*)'` | PROJECT CODE / 3RD-PARTY | Code dùng feature IL2CPP không dựng được (generic sâu, reflection, `System.Reflection.Emit`) | Log nêu thẳng method. Nếu thuộc `Assets/` → code nhà mình. Nếu thuộc DLL bên thứ ba → 3RD-PARTY |
| `il2cpp\.exe did not run properly` · `il2cpp\.exe.*exited with code` | ENVIRONMENT / PROJECT CODE | Rất mơ hồ. Có 3 nguyên nhân phổ biến: hết RAM, đường dẫn quá dài (Windows), hoặc antivirus chặn | Đọc phần stderr in ngay dưới. Không có gì cụ thể → gắn `Phỏng đoán`, gợi ý thử build lại với đường dẫn ngắn + tắt antivirus real-time |
| `Unable to convert managed assembly to C\+\+` | 3RD-PARTY | Assembly bên thứ ba dùng IL mà IL2CPP không hỗ trợ | Cập nhật/loại bỏ assembly đó |
| `System\.Reflection\.Emit .* not supported` | PROJECT CODE / 3RD-PARTY | Dynamic code generation không chạy trên AOT | Thay bằng giải pháp không dùng Emit (hay gặp ở lib serialize/DI cũ) |
| `Burst/IL2CPP` + `out of memory` | ENVIRONMENT | Máy build thiếu RAM | Giảm số job, đóng app khác, build trên máy khoẻ hơn |

## 7. Burst

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Burst error BC(\d+)` | PROJECT CODE | Job/method gắn `[BurstCompile]` dùng managed object, string, hoặc try/catch | Mã BC nói rõ vi phạm gì (BC1091 managed type, BC1042 …). Sửa code job cho thuần blittable |
| `Burst compiler .* internal compiler error` | 3RD-PARTY | Bug của Burst package với code cụ thể | Thử tắt Burst cho method đó bằng `[BurstCompile(CompileSynchronously = false)]`, hoặc update package |
| `Burst .* failed to find LLVM` | ENVIRONMENT | Cài đặt Burst hỏng | Reimport package Burst |

## 8. UnityLinker / managed stripping

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `UnityLinker .* failed` · `Failed running .*UnityLinker` | PROJECT CONFIG | `link.xml` sai cú pháp, hoặc assembly khai trong link.xml không tồn tại | Đọc stderr; sửa/xoá entry hỏng trong `link.xml` |
| `Managed Stripping Level` + error | PROJECT CONFIG | Strip quá tay, mất type mà reflection cần | Hạ Managed Stripping Level, hoặc `[Preserve]` / khai trong `link.xml` |
| `error: Assembly .* not found while resolving` (trong bước linker) | PROJECT CONFIG | link.xml trỏ tới assembly đã xoá | Cập nhật link.xml |

Lưu ý: lỗi do stripping thường **không** làm fail build mà làm crash runtime. Nếu build fail ở đây,
gần như luôn là cú pháp `link.xml`.

## 9. Addressables / Scriptable Build Pipeline

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `SBP Error` · `Build failed for .* : ` | PROJECT CONFIG | Addressables group trỏ tới asset đã xoá, hoặc chưa build content trước khi build player | Build Addressables content trước; kiểm tra group settings |
| `Addressables .* Unable to load asset` khi build | PROJECT CONFIG | Entry trỏ GUID không còn | Clean & rebuild Addressables |
| `Exception: Unable to find build of type` | PROJECT CONFIG | Build script Addressables bị thiếu sau khi update package | Reset Addressables Settings |

## 10. Môi trường & license

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `No valid Unity Editor license found` · `License is not active` | ENVIRONMENT | Hết hạn / chưa activate (rất hay gặp trên CI) | Activate lại license; trên CI dùng `-manualLicenseFile` hoặc Unity Licensing Server |
| `There is not enough space on the disk` · `No space left on device` | ENVIRONMENT | Hết ổ đĩa | Dọn `Library/`, `Temp/`, `Builds/` |
| `Unable to write file .* Access is denied` · `Sharing violation` | ENVIRONMENT | File đang bị process khác giữ (Unity mở 2 lần, antivirus, Explorer) | Đóng process giữ file; loại thư mục project khỏi antivirus |
| `The process cannot access the file because it is being used by another process` | ENVIRONMENT | Như trên | |
| `Multiple Unity instances cannot open the same project` | ENVIRONMENT | Đang mở project ở nơi khác / lock còn sót | Xoá `Temp/UnityLockfile` sau khi chắc không còn Unity nào chạy |

---

## Warning nào đáng lo (dùng cho Mode 2)

Mode 2 dễ sa vào việc liệt kê hàng trăm warning vô hại. Thang đánh giá:

| Mức | Gồm | Vì sao |
|---|---|---|
| 🟠 RISKY | `warning CS0618`/`CS0619` (obsolete) khi API sẽ bị **xoá** ở bản Unity kế · `uses-sdk:minSdkVersion` · `will be removed in a future release` · warning về stripping/`[Preserve]` · `Script attached to .* is missing` | Sẽ thành lỗi chặn build hoặc crash runtime trong tương lai gần |
| 🟡 NOTABLE | `warning CS0414` (field gán mà không dùng) · `warning CS0168`/`CS0219` (biến khai không dùng) · shader variant warning · texture không power-of-two | Bẩn code / tốn dung lượng, không gây fail |
| ⚪ NOISE | Warning từ `Library/PackageCache/`, `Packages/`, hoặc SDK bên thứ ba · warning lặp hàng trăm lần từ cùng một file package | Không sửa được bằng code của mình → không đáng đưa lên đầu bảng |

**Cầu nối bắt buộc sang Mode 1:** kiểm tra `warnaserror`, `csc.rsp`, `treatWarningsAsErrors` trong log
hoặc trong `Assets/csc.rsp`. Nếu bật thì mọi `warning CS` trong code project **chính là lỗi chặn build**
và phải xếp 🔴 BLOCKER ở Mode 1, không được để lại Mode 2.
