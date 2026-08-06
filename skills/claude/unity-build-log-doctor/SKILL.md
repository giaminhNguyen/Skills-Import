---
name: unity-build-log-doctor
description: "Chẩn đoán log build Unity thất bại (Android/iOS): khoanh đúng vùng lần build cuối trong log 20–200MB, tìm ROOT CAUSE thật (không phải lỗi cascade), phân nhóm PROJECT CODE / PROJECT CONFIG / 3RD-PARTY / ENVIRONMENT rồi in báo cáo bảng tiếng Việt. USE WHEN người dùng nhắc tới: build fail, build lỗi, build hỏng, không build được, build xong báo lỗi, check/đọc log build, Editor.log, Editor-prev.log, log Jenkins/CI, gradleOut, 'Gradle build failed', 'FAILURE: Build failed', AAPT / R8 / D8 / dex error, Duplicate class, keystore hay signing lỗi, 'xcode build failed', xcodebuild error, duplicate symbol, provisioning profile, 'Multiple commands produce', IL2CPP error, il2cpp.exe exited, Burst error BC, UnityLinker / stripping, shader error lúc build, Unity crash log — kể cả khi họ chỉ paste một đoạn log rồi hỏi 'lỗi gì đây', 'sao build không được', 'máy em chạy ngon mà lên CI fail'. Invoke tay: /unity-build-log-doctor [đường dẫn log]."
user-invocable: true
argument-hint: "[đường dẫn file log build, vd 'C:\\Users\\me\\AppData\\Local\\Unity\\Editor\\Editor-prev.log']"
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Write
related: [deep-analysis]
---

# Unity Build Log Doctor

Đọc log build Unity thất bại, khoanh đúng chỗ chết, trả về báo cáo bảng tiếng Việt.

Log build Unity có thể từ **2MB (log CI) tới 200MB (Editor.log tích luỹ)**, phần lớn là noise: import asset, shader compile, licensing, memory dump. Toàn bộ skill này xoay quanh một ý: **tìm đúng vài trăm dòng cần thiết rồi dừng**. Đọc lan man vừa tốn token vừa cho kết quả tệ hơn — vì bạn sẽ nhặt phải lỗi của lần build cũ đã fix xong từ đời nào.

---

## Đầu vào

Path lấy từ argument. Không có argument thì hỏi user, kèm gợi ý vị trí mặc định:

| Loại log | Vị trí |
|---|---|
| Unity Editor (Windows) | `%LOCALAPPDATA%\Unity\Editor\Editor.log` · `Editor-prev.log` |
| Unity Editor (macOS) | `~/Library/Logs/Unity/Editor.log` |
| Gradle (Android) | `<project>/Temp/gradleOut/` · `<project>/Logs/` |
| Xcode (iOS) | output của `xcodebuild` (thường user tự redirect ra file) |
| CI / Jenkins / Cloud Build | file do `-logFile` chỉ định, vd `Build/Logs/Build-Client.Android.log` |

Cho phép user **paste thẳng nội dung log** nếu không có file — khi đó bỏ qua Bước 0, làm việc trên đoạn đã paste và nói rõ báo cáo chỉ dựa trên phần user đưa.

**Path truyền vào tool phải là đường dẫn tuyệt đối đã expand.** `%LOCALAPPDATA%`, `~`, `$HOME` không tự expand trong tool — tự thay bằng giá trị thật trước khi gọi. Có khoảng trắng thì quote.

---

## Ba chế độ

| Mode | Việc | Khi nào chạy |
|---|---|---|
| **1 — ERROR** | Tìm lỗi chặn build | **Mặc định — chạy luôn, không hỏi** |
| **2 — WARNING** | Quét warning đáng chú ý | User chọn, hoặc Mode 1 ra 0 lỗi |
| **3 — FIX** | Đưa cách sửa | **Chỉ khi user đồng ý** |

Mặc định chạy thẳng Mode 1. Chỉ hỏi mode ở đầu khi câu của user thật sự mơ hồ giữa "tìm lỗi" và "soi warning" — hỏi một câu thừa ở đầu làm chậm đúng cái mà skill này tồn tại để làm nhanh. In bảng xong thì hỏi user có muốn xuất cách fix không.

Không tự động fix, không tự sửa code khi chưa được đồng ý — dev cần nhìn chẩn đoán trước rồi mới quyết định đụng vào đâu. Mode 1 và 2 là **read-only tuyệt đối**: thứ duy nhất được ghi là file báo cáo, và chỉ khi user đồng ý.

---

## Ngân sách

- **≤ 12 tool call** và **≤ 1500 dòng log đọc** cho một lần chạy. Đọc SKILL.md và `references/*.md` **không tính** vào ngân sách; mọi lệnh chạm vào file log thì có.
- **Không bao giờ Read nguyên file log.**
- **Đếm trước, đọc sau** (Bước 4).
- Mỗi pattern grep chạy **đúng 1 lần**. Không grep lại pattern đã chạy.
- **Dừng ngay khi root cause đã rõ.** Không quét nốt các pattern còn lại "cho chắc".
- Không dump raw log vào output — mỗi lỗi trích **tối đa 3 dòng** log gốc.
- Không spawn subagent cho việc đọc log (subagent phải đọc lại từ đầu, đắt gấp đôi).

**Ngân sách byte, không chỉ ngân sách dòng.** Log Unity có những dòng đơn dài hàng nghìn ký tự — `##utp:{...}` JSON, `## CmdLine:` của csc, đường dẫn Bee. In 200 dòng như vậy là vượt trần 32KB của tool, output bị cắt và bạn mất trắng một lượt gọi. **Luôn truncate mỗi dòng khi in một khoảng** (xem idiom bên dưới).

---

## Bộ công cụ PowerShell

Phân công dứt khoát, đừng phân vân giữa hai tool:

- **Đụng vào file log → PowerShell.** Grep tool không giới hạn được theo khoảng dòng, không lấy được match cuối, không gom hit theo pattern, và không truncate dòng dài.
- **Đụng vào source code của project → Grep tool.** Nhanh hơn, kết quả bấm được.

**Đo file** (stream, không load vào RAM):

```powershell
$p='C:\...\log'; $n=0; foreach($l in [System.IO.File]::ReadLines($p)){$n++}
"{0:N0} bytes / {1:N0} dòng" -f (Get-Item $p).Length, $n
```

**Đọc header** (nhận dạng loại log, encoding, ANSI, argv):

```powershell
Get-Content $p -TotalCount 60 | ForEach-Object { if($_.Length -gt 200){$_.Substring(0,200)}else{$_} }
```

**Histogram pattern — idiom quan trọng nhất của skill này.** Một lượt cho biết pattern nào có mặt, mỗi cái bao nhiêu lần, và dòng đầu tiên ở đâu:

```powershell
Select-String -Path $p -Pattern 'error CS\d+|IL2CPP error|Burst error BC|BuildFailedException|FAILURE: Build failed|Execution failed for task|Error building Player|Build Finished, Result:' -AllMatches |
  ForEach-Object { [pscustomobject]@{ Key=$_.Matches[0].Value; Line=$_.LineNumber } } |
  Group-Object Key |
  ForEach-Object { "{0,-45} x{1,-6} dòng đầu: {2}" -f $_.Name, $_.Count, $_.Group[0].Line }
```

`Grep` với `output_mode: count` chỉ trả **một con số cho cả file** — vô dụng khi bạn chỉ có một file log. Dùng histogram trên.

**Đọc một khoảng dòng, có số dòng thật, có truncate, dừng sớm:**

```powershell
$from=18660; $to=18840; $i=0
foreach($l in [System.IO.File]::ReadLines($p)){
  $i++
  if($i -gt $to){ break }
  if($i -ge $from){ if($l.Length -gt 200){ "$i : " + $l.Substring(0,200) + ' …[cắt]' } else { "$i : $l" } }
}
```

**Lấy match cuối cùng** (Select-String trả theo thứ tự từ đầu file):

```powershell
Select-String -Path $p -Pattern '<pattern>' | Select-Object -Last 3 | ForEach-Object { "$($_.LineNumber): $($_.Line)" }
```

---

# QUY TRÌNH

## Bước 0 — Nhận dạng loại log (làm trước mọi thứ)

Đọc 60 dòng đầu. **Loại log quyết định toàn bộ các bước sau**, nên nhầm ở đây là hỏng cả bài.

| Dấu hiệu trong header | Loại | Hệ quả |
|---|---|---|
| `Batch mode: YES`, có khối `COMMAND LINE ARGUMENTS:` với `-batchmode` / `-quit` / `-logFile` / `-executeMethod` | **Log CI / batchmode** (Jenkins, Cloud Build, script build) | **Một file = đúng một lần build.** Bỏ hẳn Bước 1.2 (khoanh biên) và 1.3 (cắt lát) — cả file là phạm vi |
| Có `Mono path[0]` / `Initialize engine version`, không có khối argv, nhiều `Refresh completed` / nhiều phiên | **Editor.log tương tác** | Có thể chứa nhiều lần build cũ → bắt buộc khoanh biên |
| Không có header Unity nào. Mở đầu thẳng bằng `> Task :` / `Starting a Gradle Daemon` / `Command line invocation:` / `note: Building targets` | **Log native thuần** (xuất từ `gradlew` hoặc `xcodebuild`) | Bỏ qua toàn bộ Stage 1–6. Vào thẳng Stage 7–8, load `android.md` hoặc `ios.md`. Không có khái niệm "nhiều lần build" trừ khi user nối nhiều lần chạy vào một file |
| Không khớp mẫu nào ở trên | **Không rõ** | Đừng ép vào khuôn. Nói với user bạn không nhận ra định dạng, hỏi log này sinh ra bằng lệnh gì, rồi làm việc theo anchor tìm được — gắn nhãn `Phỏng đoán` nếu phải suy luận |

Khối `COMMAND LINE ARGUMENTS:` của log CI là mỏ vàng, đọc nó là biết ngay: platform (`-buildTarget iOS`), hàm build được gọi (`-executeMethod Widogame.Editor.WDGBuilder.Build`), output path, keystore, buildNumber. **Đây là cách detect platform đáng tin nhất** — đáng tin hơn nhiều so với grep `BuildTarget` trong thân log (thứ hay dính vào đường dẫn package cache).

**Encoding & ANSI.** Nếu file UTF-16 (hay gặp trên Windows) hoặc chứa escape code `\x1b[` (log CI/Gradle/Xcode có màu), mọi pattern neo đầu dòng phải cho phép prefix `(\x1b\[[0-9;]*m)*` hoặc **bỏ neo `^` đi**. Regex trượt vì mã màu là lỗi im lặng — grep trả 0 hit và bạn tưởng là không có lỗi.

**Đo file.** Lấy size + tổng số dòng. Con số này quyết định đường đi:

Hai câu hỏi độc lập nhau, đừng gộp làm một: **(a) log có chứa nhiều lần build không?** và **(b) log có to tới mức phải cắt lát không?**

| | Một lần build (CI / native / Editor.log mới mở) | Nhiều lần build (Editor.log tích luỹ) |
|---|---|---|
| **< 30.000 dòng** | Fast path: grep thẳng cả file, bỏ Bước 1.2 + 1.3 | Khoanh biên (1.2), khỏi cắt lát (1.3) |
| **≥ 30.000 dòng** | Khỏi khoanh biên, nhưng **luôn dùng histogram + đọc theo khoảng**, không đọc tuần tự | Full path: khoanh biên (1.2) **và** cắt lát (1.3) |

Log CI thường nhỏ (vài MB) nhưng **không phải luôn luôn** — một job CI build nhiều target, hoặc bật log verbose Gradle, vẫn ra file hàng trăm MB. Quyết định theo hai câu hỏi trên, đừng suy ra kích thước từ loại log.

## Bước 1 — Khoanh phạm vi (chỉ khi Bước 0 nói là cần)

**1.1 — Chọn file.** Có cả `Editor.log` và `Editor-prev.log` thì so `LastWriteTime`. Lưu ý: nếu user **đã tắt/mở lại Unity sau khi build fail**, log của lần fail nằm ở `Editor-prev.log`, không phải `Editor.log`. Không chắc thì hỏi, không đoán.

**1.2 — Khoanh biên lần build cuối.** `Editor.log` cộng dồn cả session nên có thể chứa nhiều lần build fail cũ **đã fix rồi**. Tìm marker bắt đầu build gần cuối file nhất.

⚠️ **Cạm bẫy đã cắn một lần rồi:** `BuildPlayer` và `BuildPlayerOptions` cũng xuất hiện trong **stack frame của `Debug.Log`** — batchmode in stacktrace cho cả log thường, nên bạn sẽ nhận về hàng loạt dòng kiểu `UnityEditor.BuildPipeline:BuildPlayer (...)` nằm giữa file, cách chỗ build bắt đầu thật hàng nghìn dòng. Lấy nhầm cái đó làm `startLine` thì **cắt mất luôn root cause**.

Marker đáng tin, theo thứ tự ưu tiên:

1. `Successfully changed project path to:` — mở đầu một phiên thật
2. `COMMAND LINE ARGUMENTS:` — mở đầu một phiên batchmode
3. `Build Finished, Result:` của lần trước đó — biên trên của lần build hiện tại
4. `*** Tundra build` / `Refresh completed`

Marker **không** đáng tin: `BuildPlayer`, `BuildPlayerOptions`, `Starting build` khi chúng nằm trong dòng có dạng stack frame (thụt đầu dòng, có `(at Assets/...cs:NN)`, có `UnityEditor.` đứng trước).

→ Ghi lại `startLine`. Mọi lệnh sau chỉ xét trong `[startLine, EOF]`. Không xác định được biên thì **nói rõ với user rằng báo cáo có thể lẫn lỗi của lần build cũ** — đừng im lặng đoán.

**1.3 — Cắt lát** (chỉ khi file rất lớn và đã có `startLine` chắc chắn). Cắt `[startLine, EOF]` ra file tạm trong scratchpad rồi làm việc trên đó:

```powershell
$src=$p; $out='<scratchpad>\lastbuild.log'; $start=1180442
$sw=[System.IO.StreamWriter]::new($out); $i=0
foreach($l in [System.IO.File]::ReadLines($src)){ $i++; if($i -ge $start){ $sw.WriteLine($l) } }
$sw.Close(); "sliced $($i-$start+1) lines"
```

Số dòng trong file lát cộng `startLine - 1` ra số dòng thật — **báo cáo luôn dùng số dòng thật** để dev nhảy tới đúng chỗ.

## Bước 2 — Bắt "neo lỗi"

| Nguồn | Anchor |
|---|---|
| Unity (chung) | `Build completed with a result of 'Failed'` · `Build Finished, Result: Failure` · `Error building Player because scripts had compiler errors` · `BuildFailedException` · `*** Tundra build failed` |
| Android/Gradle | `FAILURE: Build failed with an exception` · `* What went wrong:` · `Execution failed for task` · `CommandInvokationFailure` · `> Task :.* FAILED` |
| iOS/Xcode | `\*\* BUILD FAILED \*\*` · `The following build commands failed` · `xcodebuild: error:` |
| Unity crash (nhánh riêng, **không phải** build fail) | `Crash!!!` · `Obtained \d+ stack frames` |

⚠️ **Đừng tin phần đuôi file.** Với log Editor tương tác thì kết luận build hay nằm gần cuối. Với **log batchmode/CI thì không**: cuối file là khối shutdown — `[Performance] Application.Shutdown.*`, `Memory Statistics`, `[ALLOC_TEMP_*]`, `##utp:{"type":"MemoryLeaks"...}`, và một dòng bẫy rất giống lỗi:

```
~StackAllocator(ALLOC_TEMP_MAIN) m_LastAlloc not NULL. Did you forget to call FreeAllStackAllocations()?
```

Dòng đó **không phải lỗi build**, nó xuất hiện ở cả build thành công. Kết luận thật (`Build Finished, Result: Failure.`) có thể nằm cách EOF cả **700 dòng**. Vì vậy: **tìm anchor bằng histogram trên cả phạm vi, đừng đọc mù 200 dòng cuối.**

Gặp anchor crash → đây là Editor/Player crash, không phải build fail: chuyển sang đọc stack frames và nói rõ với user đây là nhánh chẩn đoán khác.

**Không có anchor nào, thành công lẫn thất bại** → build bị kill / log bị cắt / build đang chạy dở. **Báo đúng như vậy, không suy diễn nguyên nhân.**

## Bước 3 — Detect platform & BUILD STAGE chết

Platform: ưu tiên khối argv ở Bước 0 (`-buildTarget`). Không có thì grep `BuildTarget` · `Scripting Backend` · `il2cpp|mono` · `xcodebuild` · `gradle`.

Xác định build dừng ở khâu nào, in vào header báo cáo, và **chỉ grep nhóm pattern của khâu đó cộng khâu liền trước**. Pattern của các khâu chưa từng chạy tới là lãng phí thuần túy — build chết ở Stage 1 thì không đời nào có lỗi Gradle.

| Stage | Marker | Nhóm pattern cần grep |
|---|---|---|
| 1. Compile C# | `Compilation failed` · `error CS` · `Script Compilation Error` · `*** Tundra build failed` | CS, asmdef, unsafe, thiếu guard `UNITY_EDITOR` |
| 2. Import asset / Shader | `Shader error in` · `AssetImportWorker` · `Import Error` | shader, texture, importer |
| 3. Build callbacks | `IPreprocessBuildWithReport` · `OnPostprocessBuild` · `BuildFailedException` | exception trong Editor script của project |
| 4. Player build | `Building Player` · `Writing data` | scene thiếu, PlayerSettings |
| 5. IL2CPP / Burst | `il2cpp.exe` · `IL2CPP error` · `Burst error BC` | il2cpp, burst |
| 6. Linker / Strip | `UnityLinker` · `Managed Stripping` | link.xml, reflection bị strip |
| 7. Gradle / Xcode | `> Task :` · `xcodebuild` · `FAILURE:` | toàn bộ pattern native của platform |
| 8. Sign & Package | `Failed to sign` · `keystore` · `provisioning` · `bundletool` | ký, profile, đóng gói |

⚠️ **Marker không xuất hiện theo đúng thứ tự 1→8.** Unity chạy `Detect Java Development Kit (JDK)`, `Detecting Android SDK`, `CheckAndroidSDK` **rất sớm**, trước cả khi compile script cho player. Thấy mấy dòng đó ở giữa file đừng vội kết luận đang ở Stage 7 — hỏi ngược lại: *có `> Task :` nào chạy chưa?* Chưa thì Gradle chưa từng khởi động.

Tương tự, hit của `keystore` rất hay đến từ **khối argv ở đầu file** (`-keystoreFileName ...`), không phải lỗi ký. Quy tắc triage: **hit nằm trước dòng build bắt đầu thật thì bỏ qua**, đừng tốn một lượt gọi để xác nhận.

**Load reference đúng lúc này, đúng một file:**

- Stage 1–6 → `references/unity-common.md`
- Stage 7–8 **Android** → `references/android.md`
- Stage 7–8 **iOS** → `references/ios.md`

Không load cả 3. Nếu thật sự cần cả common lẫn native (vd IL2CPP fail *bên trong* Gradle task), load common trước, chỉ load file platform khi common không giải thích được.

## Bước 4 — Đếm trước, đọc sau

**Không bao giờ grep chữ `error` trần** — log Unity có hàng nghìn dòng chứa từ đó, chủ yếu là tên file kiểu `.../Exceptions/IapException.cs`.

Chạy **một** histogram (idiom ở trên) cho cả cụm pattern của stage. Pattern > 200 hit = noise, bỏ. Chỉ đọc content quanh dòng của pattern có hit hợp lý, dùng idiom đọc khoảng có truncate.

Cụm tối thiểu cho histogram đầu tiên:

```
error CS\d+|Shader error in|IL2CPP error|Burst error BC|BuildFailedException|
FAILURE: Build failed|Execution failed for task|xcodebuild: error:|
The following build commands failed|Failed to sign|CommandInvokationFailure|
Error building Player|Build Finished, Result:
```

Bảng pattern chi tiết nằm trong `references/` (đã load ở Bước 3).

**Bảng pattern là danh sách ca thường gặp, không phải danh sách đầy đủ.** Unity, AGP, Xcode và mỗi SDK quảng cáo đẻ ra thông báo lỗi mới liên tục; sẽ có những lần log không khớp dòng nào trong `references/`. Đó là chuyện bình thường, **không phải** lý do để ép lỗi vào một hàng gần đúng rồi báo như thật. Histogram ra 0 hit hoặc chỉ ra toàn hit vô nghĩa → đi thẳng vào nhánh fallback ở mục **ĐỘ TIN CẬY**: đọc 60 dòng trước anchor thất bại, suy luận, gắn nhãn `Phỏng đoán`, nói rõ là không khớp pattern đã biết. Một chẩn đoán trung thực kèm chữ "chưa chắc" có ích hơn nhiều một chẩn đoán sai kèm chữ "chắc chắn".

## Bước 5 — Xác định ROOT CAUSE, không liệt kê hết

Một build fail sinh ra rất nhiều dòng đỏ nhưng thường chỉ có **một** nguyên nhân. Việc của bạn là chỉ ra nó, không phải chép lại toàn bộ.

- Lỗi **đầu tiên theo thời gian** thường là gốc; lỗi sau đa số là hệ quả (cascade).
- **Gradle**: chuỗi `Caused by:` **cuối cùng** mới là nguyên nhân thật, không phải dòng đầu.
- **Xcode**: dòng `error:` **đầu tiên trong task fail**, không phải dòng tổng kết cuối.
- **Bee/Tundra (Unity 2021+)**: backend in **lại nguyên khối output của csc một lần cho mỗi assembly target** (`Assembly-CSharp.dll (+2 others)`). Cùng một lỗi sẽ xuất hiện 2–3 lần ở các dòng cách xa nhau, kèm nguyên list warning lặp lại. **Dedupe theo bộ ba (file, dòng, mã lỗi)**, không theo số lần xuất hiện — nếu không bạn sẽ báo 3 lỗi trong khi chỉ có 1.
- Gộp lỗi lặp thành 1 dòng + đếm số lần (`x12`), không in trùng.
- Trần cứng: tối đa **8 lỗi chính** (Mode 1), **12 nhóm warning** (Mode 2). Phần dư gom vào một dòng "… và N mục tương tự".

## Bước 6 — Đối chiếu source (chỉ khi lỗi thuộc code project)

Log chỉ ra `Assets/...cs:line` → Read đúng vùng **±15 dòng** quanh đó.

⚠️ **Số dòng trong log và số dòng trong file hiện tại có thể lệch nhau.** CI build từ một commit khác với working tree đang sửa dở. Nếu đọc ±15 dòng mà không thấy token mà log nhắc tới, **nới ra ±30 và nói rõ độ lệch trong báo cáo** ("log ghi dòng 195, file hiện tại nằm ở dòng 194") — đừng im lặng báo sai vị trí, dev sẽ nhảy vào nhầm hàm.

**Được phép thêm đúng một lượt tra cứu symbol** khi lỗi thuộc dạng "không tìm thấy tên": `CS0117`, `CS1061`, `CS0246`, `CS0103`. Đọc ±15 dòng chỉ cho biết *cái tên đó sai*, không cho biết *tên đúng là gì* — mà tên đúng mới là thứ dev cần. Một lệnh Grep tìm khai báo thật hoặc call site anh em thường biến "member `data` không tồn tại" thành "phải là `Data`, chữ D hoa" — khác nhau một trời một vực về mức hữu ích.

## Bước 7 — Đối chiếu git (1 lệnh, tín hiệu rất mạnh)

Với lỗi nhóm `PROJECT CODE` / `PROJECT CONFIG`, kiểm tra file đó có nằm trong `git status` hoặc `git log -3 --name-only` không. Có → đánh dấu 🔥 `vừa sửa gần đây` trong bảng. "File này bạn vừa động vào" thường là câu trả lời nhanh nhất cho "sao hôm qua build được mà hôm nay không". Chỉ 1 lệnh git, không quét lịch sử sâu.

---

# PHÂN NHÓM & ƯU TIÊN

Mỗi nhóm cần một cách xử lý khác nhau — đây là lý do phải phân nhóm chứ không chỉ để cho đẹp bảng:

| Nhóm | Gồm | Cách xử lý |
|---|---|---|
| **PROJECT CODE** | C# gameplay, Editor script, build callback | **Đào sâu** — được Read source |
| **PROJECT CONFIG** | PlayerSettings, asmdef, gradle template, AndroidManifest, Info.plist, keystore, signing, scripting backend | **Đào sâu** — được Read file config |
| **3RD-PARTY** | Xung đột plugin/SDK | Chỉ ra **plugin nào, version nào đụng nhau**. **KHÔNG đọc source thư viện**, không mở file trong `Library/`, `Packages/`, `Pods/`. Chỉ đào sâu khi user yêu cầu rõ ("tìm sâu vào thư viện") |
| **ENVIRONMENT** | JDK/SDK/NDK/Gradle version, dung lượng đĩa, RAM, mạng, path quá dài, license | Ghi rõ **cần cài/đổi gì**. **Không coi là lỗi code**, không sửa file dự án |

## Nhóm ưu tiên SỐ 1 — Build callback của project

Exception ném ra từ `IPreprocessBuildWithReport` / `IPostprocessBuildWithReport` / `[PostProcessBuild]` / `OnPostprocessBuild` là **code do dev trong team viết** → luôn xếp 🔴 BLOCKER, luôn phân tích sâu (được Read Editor script tương ứng).

Đây là nguyên nhân build fail rất phổ biến nhưng hay bị bỏ qua, vì stacktrace đi qua `UnityEditor.BuildPipeline` nên **trông y hệt lỗi engine**. Thấy stack có tên namespace của project → đó là code nhà mình.

**Nhưng đừng bắt nhầm:** trong batchmode, Unity in stacktrace cho **cả `Debug.Log` thường**. Một khối stack chứa `UnityEditor.BuildPipeline:BuildPlayer` + `OnPreprocessBuild` có thể chỉ là log "Preprocessing completed." vô hại. Phân biệt bằng dòng **ngay trên** stack: có `Exception`/`error` thì là lỗi thật; là câu thông báo bình thường thì bỏ qua.

---

# ĐỘ TIN CẬY

Mọi dòng bảng phải có nhãn:

| Nhãn | Nghĩa |
|---|---|
| `Chắc chắn` | Log nêu thẳng nguyên nhân |
| `Nhiều khả năng` | Khớp pattern đã biết, suy ra |
| `Phỏng đoán` | Không khớp pattern nào, đọc ngữ cảnh mà đoán |

**Không bao giờ trình bày `Phỏng đoán` bằng giọng khẳng định.** Dev sẽ đi sửa theo lời bạn; một phỏng đoán được nói như sự thật khiến họ mất cả buổi sửa nhầm chỗ.

**Fallback khi không khớp pattern nào:** lấy 60 dòng ngay trước anchor thất bại, đọc và suy luận, gắn nhãn `Phỏng đoán`, nói rõ "không khớp pattern đã biết". **Cấm bịa nguyên nhân cho có.**

**Cầu nối Mode 1 ↔ Mode 2:**
- Mode 1 phải kiểm tra `warnaserror` / `csc.rsp` / `treatWarningsAsErrors`. Bật → một `warning CS` **chính là** lỗi chặn build, xếp BLOCKER.
- Mode 1 ra 0 lỗi mà build vẫn fail → gợi ý chạy Mode 2 và kiểm tra khả năng log bị cắt.

---

# ĐỊNH DẠNG OUTPUT

Toàn bộ báo cáo **tiếng Việt**, thuật ngữ kỹ thuật giữ nguyên tiếng Anh. Bảng markdown, ô ngắn (≤ ~60 ký tự, rút gọn chứ không xuống dòng bừa). Không emoji ngoài bộ badge mức độ và 🔥.

Mở đầu bằng khối tóm tắt:

```
┌ UNITY BUILD LOG DOCTOR ────────────────────────────
│ Platform : Android (IL2CPP, ARM64)
│ Log      : Editor.log · 84 MB · 1.204.331 dòng
│ Phạm vi  : lần build cuối, dòng 1.180.442 → EOF
│ Chết tại : Stage 7 — Gradle · task :launcher:mergeReleaseResources
│ Kết quả  : 1 lỗi chặn · 3 lỗi hệ quả · 7 warning
└────────────────────────────────────────────────────
```

**Bảng Mode 1** — cột: `#` | `Mức` | `Key / Mã lỗi` | `Vị trí` | `Nguyên nhân` | `Nhóm` | `Tin cậy`
- `Mức`: 🔴 BLOCKER / 🟠 MAJOR / 🟡 CASCADE
- `Key`: mã hoặc chuỗi định danh (`error CS0246`, `Duplicate class`, `ld: symbol not found`…)
- `Vị trí`: `file:line` nếu có, **kèm số dòng trong log** (`log:#845121`) để dev tự nhảy tới. Thêm 🔥 nếu file vừa sửa gần đây (Bước 7)

Ngay dưới bảng là **"Giải thích chi tiết"**: mỗi lỗi BLOCKER một block ngắn theo mạch *Chuyện gì xảy ra → Vì sao → Ảnh hưởng*, kèm trích **tối đa 3 dòng** log gốc trong code block.

Nếu lỗi thuộc dạng "chạy trong Editor thì ngon, lên build/CI mới chết", **giải thích luôn vì sao** — đó chính là câu hỏi thật sự trong đầu dev, kể cả khi họ không hỏi thành lời. Xem `unity-common.md` §1 (guard `#if UNITY_EDITOR`, define theo platform).

**Bảng Mode 2** — cột: `#` | `Mức` | `Key` | `Vị trí` | `Số lần` | `Ý nghĩa` | `Có nên sửa?`
- `Mức`: 🟠 RISKY (dễ thành lỗi runtime / sắp deprecated chặn build) / 🟡 NOTABLE / ⚪ NOISE
- Gom warning trùng theo key, **sắp xếp giảm dần theo rủi ro**, không theo thứ tự xuất hiện

**Không tìm thấy lỗi nào:** nói thẳng "không tìm thấy lỗi chặn trong log", liệt kê pattern đã quét, gợi ý log/bước tiếp theo cần lấy. **Không đoán bừa nguyên nhân.**

Cuối báo cáo: hỏi user có muốn lưu ra `Logs/build-report-<yyyyMMdd-HHmm>.md` để gửi team không.

## Báo cáo mẫu

````markdown
┌ UNITY BUILD LOG DOCTOR ────────────────────────────
│ Platform : Android (IL2CPP, ARM64)
│ Log      : Editor-prev.log · 46 MB · 612.884 dòng
│ Phạm vi  : lần build cuối, dòng 588.120 → EOF
│ Chết tại : Stage 7 — Gradle · task :launcher:checkReleaseDuplicateClasses
│ Kết quả  : 1 lỗi chặn · 1 lỗi hệ quả · 2 warning
└────────────────────────────────────────────────────

### Lỗi chặn build

| # | Mức | Key / Mã lỗi | Vị trí | Nguyên nhân | Nhóm | Tin cậy |
|---|---|---|---|---|---|---|
| 1 | 🔴 BLOCKER | `Duplicate class com.google.android.gms.ads.*` | log:#601442 | play-services-ads có trong cả AdMob SDK lẫn plugin MAX | 3RD-PARTY | Chắc chắn |
| 2 | 🟡 CASCADE | `Execution failed for task ':launcher:checkReleaseDuplicateClasses'` | log:#601905 | Hệ quả trực tiếp của #1 | 3RD-PARTY | Chắc chắn |

### Giải thích chi tiết

**#1 — Duplicate class (3RD-PARTY)**

*Chuyện gì xảy ra*: Gradle dừng ở bước kiểm tra class trùng, thấy `com.google.android.gms.ads` xuất hiện trong hai artifact khác nhau.

*Vì sao*: `Assets/Plugins/Android/mainTemplate.gradle` khai `play-services-ads:22.6.0`, trong khi AppLovin MAX adapter kéo theo `play-services-ads:23.0.0` — hai bản cùng nằm trong classpath.

*Ảnh hưởng*: chặn hoàn toàn ở Stage 7, không sinh được APK/AAB.

```
> Task :launcher:checkReleaseDuplicateClasses FAILED
Duplicate class com.google.android.gms.ads.AdRequest found in modules
  play-services-ads-22.6.0.aar and play-services-ads-23.0.0.aar
```

### Warning đáng chú ý

| # | Mức | Key | Vị trí | Số lần | Ý nghĩa | Có nên sửa? |
|---|---|---|---|---|---|---|
| 1 | 🟠 RISKY | `uses-sdk:minSdkVersion 22 cannot be smaller` | log:#599310 | x1 | SDK yêu cầu minSdk 23, hiện đang 22 | Nên — sẽ chặn build sau khi fix #1 |
| 2 | 🟡 NOTABLE | `warning CS0618: 'Object.FindObjectOfType' is obsolete` | `Assets/_Project/Scripts/Game/ScoreController.cs:88` | x4 | API deprecated, Unity 6 sẽ bỏ | Có thể để sau |

Bạn có muốn mình xuất **cách fix** (Mode 3) cho các lỗi trên không?
````

---

# MODE 3 — Cách fix

Với mỗi lỗi đưa ra ba phần: **Fix nhanh** (làm ngay được) → **Fix đúng** (xử lý gốc) → **Cách verify** (build lại thế nào để biết đã hết). Nêu rõ file/setting cần đụng tới.

Nhóm `ENVIRONMENT` thì **chỉ hướng dẫn, không sửa file dự án**. Fix cần sửa code project thì **hỏi xác nhận trước khi sửa**.

## Ràng buộc khi sửa code trong repo này

Trước khi đề xuất hay thực hiện bất kỳ sửa đổi nào, đọc `CLAUDE.md` của dự án và tuân thủ:

- Field serialized mới phải có `[Tooltip("...")]` tiếng Việt.
- Không `Object.Instantiate` prefab từ `PrefabDataSO` — dùng SimplePool.
- Số hiển thị cho người chơi phải lerp, không gán thẳng.
- **`Assets/_Project/Scripts/Toppic/` là base code dùng chung: PHẢI hỏi xác nhận trước khi sửa**, ưu tiên giải pháp không đụng base.

---

# Tuỳ chọn

**Xuất báo cáo ra file** — user đồng ý thì Write ra `Logs/build-report-<yyyyMMdd-HHmm>.md` (nội dung y hệt báo cáo đã in).

**Diff với log build thành công gần nhất** — chỉ dùng khi log fail không đưa ra được nguyên nhân rõ ràng (toàn `Phỏng đoán`). So phần đầu hai log để tìm chỗ rẽ nhánh: version Unity/Gradle/JDK, danh sách package, PlayerSettings. Không diff toàn file — chỉ grep vài dòng version ở cả hai bên.
