# Reference — Android (Gradle / AAPT / D8 / R8 / signing)

Chỉ load file này khi build chết ở **Stage 7–8 trên Android**. Lỗi C#, shader, IL2CPP, Burst, linker
nằm ở `unity-common.md` — Gradle không đụng tới chúng.

Với Android, thứ tự đọc luôn là: `> Task :... FAILED` (chết ở task nào) → `* What went wrong:` →
chuỗi `Caused by:` **cuối cùng**. Dòng `FAILURE: Build failed with an exception` chỉ là tiêu đề, không
bao giờ chứa nguyên nhân.

## Mục lục

- [Cụm pattern cho lượt count đầu tiên](#cụm-pattern-cho-lượt-count-đầu-tiên)
- [1. Toolchain: JDK / Gradle / AGP / Kotlin](#1-toolchain-jdk--gradle--agp--kotlin)
- [2. Manifest merger](#2-manifest-merger)
- [3. Dex / D8 / R8](#3-dex--d8--r8)
- [4. Resource / AAPT](#4-resource--aapt)
- [5. Dependency resolution](#5-dependency-resolution)
- [6. Signing & keystore](#6-signing--keystore)
- [7. SDK / NDK / môi trường máy](#7-sdk--ndk--môi-trường-máy)
- [8. Đóng gói AAB / Play Asset Delivery](#8-đóng-gói-aab--play-asset-delivery)
- [Đọc `CommandInvokationFailure` cho đúng](#đọc-commandinvokationfailure-cho-đúng)

---

## Cụm pattern cho lượt count đầu tiên

Chạy một lượt `output_mode: count` với cụm này trước khi lấy content bất cứ thứ gì:

```
Unsupported class file major version|Namespace not specified|Manifest merger failed|Duplicate class|Program type already present|Cannot fit requested classes in a single dex|Missing classes detected while running R8|resource linking failed|AAPT: error:|Could not resolve|Could not find|Failed to sign|keystore|Unable to locate Android SDK|NDK not found|OutOfMemoryError|uses-sdk:minSdkVersion|Execution failed for task
```

Pattern nào > 200 hit là noise (`keystore` hay dính vào log cấu hình) — bỏ, đừng lấy content.

---

## 1. Toolchain: JDK / Gradle / AGP / Kotlin

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Unsupported class file major version (\d+)` | PROJECT CONFIG | JDK Unity dùng quá mới/cũ so với Gradle plugin. major 65=JDK21, 61=JDK17, 55=JDK11 | Trỏ **External Tools → JDK** về bản Unity khuyến nghị (Unity 2022 → JDK 11; Unity 6 → JDK 17). Bỏ tick "Use JAVA_HOME" nếu máy có JDK lạ |
| `Namespace not specified` · `Please specify a namespace in the module's build.gradle` | 3RD-PARTY | AGP 8+ bắt buộc `namespace`, plugin/AAR cũ chỉ có `package` trong manifest | Update plugin lên bản hỗ trợ AGP 8, hoặc thêm `namespace "com.x.y"` vào `build.gradle` của module đó. Không hạ AGP nếu Unity ghim version |
| `supports only Kotlin Gradle plugin version .* or higher` | 3RD-PARTY | SDK kéo theo Kotlin plugin mới hơn bản Unity template khai | Nâng `kotlin_version` trong `baseProjectTemplate.gradle` cho khớp yêu cầu SDK |
| `Minimum supported Gradle version is .*\. Current version is` | PROJECT CONFIG | `gradle-wrapper.properties` custom bị lệch với AGP | Sửa distributionUrl về đúng cặp AGP↔Gradle, hoặc bỏ template custom cho Unity tự sinh |
| `Could not compile settings file` · `Could not compile build file` | PROJECT CONFIG | Cú pháp sai trong `*Template.gradle` do sửa tay | Đọc dòng `Caused by:` cuối — nó chỉ thẳng số dòng trong file template |
| `No matching variant of .* was found` · `requires at least a Java (\d+)` | 3RD-PARTY | Thư viện build bằng JDK cao hơn JDK đang chạy Gradle | Nâng JDK, hoặc ghim thư viện về bản cũ hơn |

## 2. Manifest merger

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Manifest merger failed : Attribute application@(\w+)` | 3RD-PARTY | Hai SDK khai cùng attribute khác giá trị (hay gặp `@name`, `@theme`, `@allowBackup`) | Thêm `tools:replace="android:<attr>"` vào `<application>` trong `AndroidManifest.xml` của LauncherManifest |
| `Manifest merger failed with multiple errors` | 3RD-PARTY | Nhiều xung đột cùng lúc | Đọc các dòng `Error:` ngay dưới — mỗi dòng là một attribute, xử lý từng cái |
| `uses-sdk:minSdkVersion (\d+) cannot be smaller than version (\d+) declared in library` | 3RD-PARTY | SDK yêu cầu minSdk cao hơn PlayerSettings | Nâng **Player Settings → Minimum API Level**. Không dùng `tools:overrideLibrary` trừ khi chắc SDK đó không chạm API mới |
| `Attribute .* value=.* is also present at .* value=` | 3RD-PARTY | Trùng khai báo giữa hai plugin | Như trên, dùng `tools:replace` cho đúng attribute log nêu |

## 3. Dex / D8 / R8

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Duplicate class ([\w.$]+) found in modules` | 3RD-PARTY | Hai SDK cùng nhúng một thư viện (hay gặp `play-services-*`, `kotlin-stdlib`, `androidx.*`) | Log nêu thẳng tên 2 module + version. Ép một version trong `mainTemplate.gradle` bằng `resolutionStrategy.force`, hoặc `exclude group:` ở dependency nào đến sau |
| `Program type already present: ([\w.$]+)` | 3RD-PARTY | Cùng bản chất với Duplicate class, thường do một AAR **và** một JAR cùng chứa class đó | Xoá file `.jar` thừa trong `Assets/Plugins/Android/`, giữ AAR |
| `Cannot fit requested classes in a single dex file` · `method ID not in \[0, 0xffff\]` | PROJECT CONFIG | Vượt trần 64K method | Bật **Multidex** (Player Settings hoặc `multiDexEnabled true`), và bật minify/R8 để cắt bớt |
| `Missing classes detected while running R8` | 3RD-PARTY | R8 shrink thấy class được tham chiếu nhưng không có trong classpath | Copy khối `-dontwarn` R8 in ra ngay bên dưới vào `Assets/Plugins/Android/proguard-user.txt`. Nếu class đó thật sự cần → thiếu dependency, phải thêm chứ không `-dontwarn` |
| `R8: ` + `java.lang.OutOfMemoryError` | ENVIRONMENT | R8 hết heap | Tăng `org.gradle.jvmargs=-Xmx4096M` trong `gradleTemplate.properties` |
| `Type ([\w.$]+) is defined multiple times` | 3RD-PARTY | Trùng class ở mức dex | Như Duplicate class |
| `Default interface methods are only supported starting with Android N` | 3RD-PARTY | Thư viện dùng Java 8+ feature mà chưa bật desugaring | Bật `coreLibraryDesugaringEnabled true` + `compileOptions` Java 8 trong template |

## 4. Resource / AAPT

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Android resource linking failed` | 3RD-PARTY | Tiêu đề chung — nguyên nhân nằm ở các dòng `AAPT: error:` ngay dưới | Luôn lấy `-C 8` quanh nó để thấy dòng AAPT thật |
| `AAPT: error: resource ([\w.:/]+) not found` | 3RD-PARTY | Theme/style/attr do SDK khai bị thiếu vì version `appcompat`/`material` lệch | Đồng bộ version `androidx.appcompat`/`com.google.android.material` trong `mainTemplate.gradle` |
| `duplicate value for resource '([\w.]+)'` | 3RD-PARTY | Hai plugin khai cùng string/color/style | Xoá bản trùng trong `Assets/Plugins/Android/res/`, giữ bản của SDK chính |
| `AAPT: error: failed to read PNG signature` · `file does not start with PNG signature` | PROJECT CONFIG | Icon/asset trong `res/` không phải PNG thật (đổi đuôi tay) hoặc bị Git LFS chưa pull | Export lại PNG chuẩn; nếu dùng LFS thì `git lfs pull` |
| `Invalid <queries> declaration` | 3RD-PARTY | SDK cũ khai `<queries>` sai chuẩn AGP mới | Update SDK; hoặc sửa manifest của plugin |
| `resource android:attr/lStar not found` | 3RD-PARTY | Kinh điển: `compileSdkVersion` < 31 nhưng thư viện androidx cần 31+ | Nâng **Target API Level** ≥ 31 |

## 5. Dependency resolution

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Could not resolve ([\w.:\-]+)` · `Could not find ([\w.:\-]+)` | 3RD-PARTY / ENVIRONMENT | Sai version, thiếu repository, hoặc mạng chặn | Đọc list "Searched in the following locations" ngay dưới. Thiếu repo → thêm `maven { url }` vào `baseProjectTemplate.gradle`. Version không tồn tại → sửa lại số |
| `Could not GET 'https://.*'` · `Connection timed out` · `peer not authenticated` | ENVIRONMENT | Mạng / proxy / firewall công ty chặn Maven | Thử lại, cấu hình proxy trong `gradle.properties`, hoặc dùng mirror nội bộ. **Không phải lỗi code** |
| `Could not download ([\w.\-]+\.aar)` · `Premature end of Content-Length` | ENVIRONMENT | Cache Gradle hỏng giữa chừng | Xoá `~/.gradle/caches/modules-2/files-2.1/<artifact>` rồi build lại |
| `Failed to apply plugin .*google-services` · `File google-services.json is missing` | PROJECT CONFIG | Firebase chưa có file config | Đặt `google-services.json` vào `Assets/` (hoặc `Assets/Plugins/Android/`) |

## 6. Signing & keystore

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Failed to sign APK` · `Failed to sign the bundle` | PROJECT CONFIG | Tiêu đề — đọc `Caused by:` để biết là sai pass hay thiếu file | Xem 2 dòng dưới |
| `keystore password was incorrect` · `Cannot recover key` | PROJECT CONFIG | Sai keystore password / key password (hai cái khác nhau!) | Nhập lại ở **Player Settings → Publishing Settings**. `Cannot recover key` = đúng keystore pass nhưng sai **key** pass |
| `Keystore file .* not found` · `Keystore file not set` | PROJECT CONFIG | Đường dẫn keystore tương đối bị lệch, hoặc file không commit (đúng vậy, keystore không nên commit) | Trỏ lại đường dẫn tuyệt đối; trên CI thì inject qua env/secret |
| `Failed to read key .* from store` | PROJECT CONFIG | Sai alias | Kiểm tra alias bằng `keytool -list -v -keystore <file>` |
| `jarsigner: unable to open jar file` | ENVIRONMENT | JDK/`jarsigner` không có trong PATH | Cài đúng JDK, trỏ lại External Tools |

## 7. SDK / NDK / môi trường máy

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `Unable to locate Android SDK` · `Android SDK not found` | ENVIRONMENT | Chưa cài module Android hoặc path SDK sai | Unity Hub → Add Modules → Android Build Support (+ SDK/NDK/JDK). Kiểm tra **External Tools** |
| `NDK not found` · `NDK is missing a "platforms" directory` | ENVIRONMENT | Thiếu NDK hoặc sai version so với Unity | Cài đúng NDK version Unity yêu cầu (mỗi bản Unity ghim một bản NDK) |
| `Failed to find target with hash string 'android-(\d+)'` | ENVIRONMENT | Chưa tải platform SDK tương ứng Target API Level | `sdkmanager "platforms;android-<n>"` hoặc tải qua Android Studio |
| `Daemon .* disappeared unexpectedly` · `java.lang.OutOfMemoryError: Java heap space` | ENVIRONMENT | Gradle daemon hết RAM | `org.gradle.jvmargs=-Xmx4096M` trong `gradleTemplate.properties`; đóng bớt app; **không phải lỗi code** |
| `The specified path, file name, or both are too long` · `path .* too long` | ENVIRONMENT | Windows MAX_PATH 260 ký tự | Chuyển project lên đường dẫn ngắn (`D:\p\`), hoặc bật LongPathsEnabled |
| `There is not enough space on the disk` · `No space left on device` | ENVIRONMENT | Hết ổ đĩa (build Android ăn vài GB temp) | Dọn `Temp/`, `Library/Bee/`, cache Gradle |
| `Gradle build daemon .* stopped` + không có lỗi nào khác | ENVIRONMENT | Daemon bị kill (antivirus, sleep, OOM hệ thống) | Build lại; nếu lặp thì tắt daemon `org.gradle.daemon=false` để lấy log rõ hơn |

## 8. Đóng gói AAB / Play Asset Delivery

| Pattern | Nhóm | Nguyên nhân thường gặp | Hướng fix chuẩn |
|---|---|---|---|
| `bundletool` + `error` | PROJECT CONFIG | Cấu hình AAB/asset pack sai | Đọc dòng bundletool cụ thể; hay gặp asset pack rỗng hoặc trùng tên |
| `Asset pack .* is empty` | PROJECT CONFIG | Khai asset pack nhưng không có asset nào được gán | Gán asset hoặc bỏ pack |
| `Files inside the base module must not exceed` | PROJECT CONFIG | Base module vượt giới hạn Play | Đẩy asset sang Play Asset Delivery / Addressables remote |

---

## Đọc `CommandInvokationFailure` cho đúng

`CommandInvokationFailure: Gradle build failed.` là cách Unity **bọc lại** lỗi Gradle — bản thân nó
không mang thông tin. Nguyên nhân thật nằm trong phần stdout của Gradle được in **ngay dưới** nó:

```
CommandInvokationFailure: Gradle build failed.
...
FAILURE: Build failed with an exception.
* What went wrong:
Execution failed for task ':launcher:checkReleaseDuplicateClasses'.
> A failure occurred while executing com.android.build.gradle.internal.tasks.CheckDuplicatesRunnable
   > Duplicate class com.google.android.gms.ads.AdRequest found in modules ...
```

Quy tắc: báo cáo phải nêu **dòng trong cùng nhất của chuỗi `>` / `Caused by:`** làm root cause, còn
`Execution failed for task` và `CommandInvokationFailure` xếp 🟡 CASCADE. Nêu `CommandInvokationFailure`
làm nguyên nhân chính là sai — nó đúng với mọi lỗi Gradle nên không nói lên điều gì.
