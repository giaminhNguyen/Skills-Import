---
name: controller-flow-design
description: "Thiết kế luồng gọi & init cho một controller mới trong tầng Game theo đúng pattern base của dự án (BaseGameManager → BaseGameController → StateGamePlayFollower, handshake 2 pha OnControllerReady + OnInitController, event bus EventManager, token lifecycle). USE WHEN thêm/thiết kế bất kỳ controller, sub-controller, follower, hub, booster, system hay coordinator nào ở tầng Game — để nó gắn đúng vào luồng init và giao tiếp đúng chuẩn. Invoke: /controller-flow-design [tên controller]."
user-invocable: true
argument-hint: "[tên/loại controller cần thiết kế, vd 'ShuffleBooster' hoặc 'ScoreController']"
allowed-tools: Read, Glob, Grep, Write, Edit
related: [gdd-spec-retrieval, plan-handoff]
---

# Controller Flow Design

Hướng dẫn thiết kế **luồng gọi & khởi tạo** cho một controller mới sao cho nó cắm đúng vào bộ khung base dùng chung (`Toppic/Base`) và giao tiếp đúng chuẩn với các controller khác. Skill này lo phần **kiến trúc luồng** (chọn base class, hook vào init flow, chọn kênh giao tiếp, vòng đời async) — không lo logic gameplay bên trong.

## Khi nào dùng

- Thêm một controller/system mới ở tầng `Assets/_Project/Scripts/Game/` (score, objective, powerup, spawner, effect…).
- Thêm một booster mới (kế thừa `BaseBoosterController`).
- Thêm một loại di chuyển mới (kế thừa `IMoveController`).
- Tách một khối logic phình to trong controller cũ ra thành controller con riêng.
- Bất cứ khi nào phân vân "cái này nên là MonoBehaviour follower hay POCO?", "init nó ở đâu?", "nó nói chuyện với controller kia bằng ref hay event?".

## Nền tảng bắt buộc nắm (base handshake)

Trước khi thiết kế, phải hiểu bộ khung này (chi tiết đầy đủ xem phần phân tích base trong hội thoại / hỏi lại nếu cần):

```
Execution order:  GameManager(-989) → RootController(-979) → Followers(0)
Awake:  Root  → OnInitController += HandleInitController
        Follower → OnControllerReady += OnControllerReady
Start:  Root.Start:
          ① OnControllerReady.Invoke(this)   [PHA 1] mọi Follower nhận ref Root (_gamePlayController)
          ② ControllerLoaded() → state 0→1 → OnInitController.Invoke()  [PHA 2]
               → Root.HandleInitController(): Initialized() → PostInitialized() → OnReady()
```

**3 hệ quả phải nhớ khi thiết kế:**
1. **Follower KHÔNG tự init.** Nó chỉ nhận ref Root qua `OnControllerReady`. Muốn nó chạy `Initialized/PostInitialized`, **Root phải gọi tường minh** → thêm follower = phải sửa Root (thêm `[SerializeField]` ref + gọi trong `Initialized`/`PostInitialized`).
2. **`Initialized` vs `PostInitialized`:** `Initialized` = dựng state của CHÍNH mình (không đọc controller khác). `PostInitialized` = được phép đọc chéo state controller khác qua `_gamePlayController` (vì pha 1 mọi con đã init xong).
3. **Runtime giao tiếp chéo qua `EventManager`**, không gọi thẳng controller khác (trừ khi đọc property qua Root facade).

## Bước 0 — Chọn archetype

| # | Archetype | Base class | Ai khởi tạo nó | Dùng khi |
|---|-----------|-----------|----------------|----------|
| 1 | **Root Controller** | `BaseGameController` | `BaseGameManager` (OnInitController) | 1 controller "cửa" của cả scene |
| 2 | **Follower** | `StateGamePlayFollower` | Root gọi tường minh trong `Initialized/PostInitialized` | System gameplay độc lập, cần vòng đời level + event |
| 3 | **Sub-follower + Hub** | `BaseBoosterController` (hoặc base tương tự) + 1 Follower làm hub | Hub gọi `Init()`+`Initialized()`+`PostInitialized()` | Nhiều biến thể cùng loại (booster, enemy…) do 1 hub route theo type |
| 4 | **POCO logic** | class thường / `interface` (vd `IMoveController`) | 1 Coordinator (không phải MonoBehaviour) build/play/stop | Logic thuần, không cần Inspector, đời sống gắn coordinator |

Cây quyết định nhanh:
- Có 1 mỗi scene, là gốc điều phối? → **Root (1)**.
- Cần `[SerializeField]` ref/Inspector + vòng đời level? → **Follower (2)**.
- Là 1 trong nhiều biến thể cùng họ, được route theo type? → **Sub-follower + Hub (3)**.
- Logic thuần, tạo/hủy theo cụm, không cần MonoBehaviour? → **POCO (4)**.

---

## Archetype 1 — Root Controller

Hiếm khi thêm mới (mỗi scene 1 cái: `GamePlayController`, `HomeController`, `LoadingController`). Skeleton:

```csharp
namespace Game
{
    public class XxxController : BaseGameController
    {
        #region PROPERTIES
        //Properties — facade expose follower cho con khác dùng chéo
        public YyyController YyyController => yyyController;
        //Serialized Fields
        [SerializeField] private YyyController yyyController;
        #endregion

        #region UNITY METHODS
        protected override void OnEnable()  { base.OnEnable();  EventManager.OnZzz += HandleZzz; }
        protected override void OnDisable() { base.OnDisable(); EventManager.OnZzz -= HandleZzz; }
        #endregion

        #region IMPLEMENT METHODS
        protected override void Initialized()
        {
            // 1) nạp data level (LevelInfo) 1 lần
            // 2) fan-out .Initialized(level) cho từng follower, ĐÚNG THỨ TỰ phụ thuộc
            yyyController.Initialized(level);
        }

        protected override void PostInitialized()
        {
            base.PostInitialized();
            yyyController.PostInitialized();   // pha đọc chéo
        }
        #endregion

        #region EVENT METHODS
        private void HandleZzz() { }
        #endregion
    }
}
```

Root là **single source of truth cho trạng thái kết thúc** (xem `GamePlayController`: `IsLevelEnded`, `TryEndLevel`, `CheckWin/LoseCondition`). Follower muốn kết thúc level thì **gọi ngược lên Root**, không tự raise `OnLevelWin/Lose`.

---

## Archetype 2 — Follower (dùng nhiều nhất)

```csharp
using _Project.Scripts.Base;
using Toppic.Data;
using Toppic.Event;
using UnityEngine;

namespace Game
{
    public class XxxController : StateGamePlayFollower
    {
        #region PROPERTIES
        //Properties
        public bool IsActive { get; private set; }
        //Serialized Fields
        [SerializeField] private float someConfig = 1f;
        //Private
        private int _state;
        #endregion

        #region UNITY METHODS
        // Wire event Ở ĐÂY (đối xứng, đảm bảo gọi) — KHÔNG wire trong OnControllerReady.
        protected override void OnEnable()
        {
            base.OnEnable();                      // BẮT BUỘC: giữ hook token của BaseBehaviour
            EventManager.OnItemsMatched += HandleItemsMatched;
            EventManager.OnLevelWin  += HandleLevelEnded;
            EventManager.OnLevelLose += HandleLevelEnded;
        }
        protected override void OnDisable()
        {
            base.OnDisable();
            EventManager.OnItemsMatched -= HandleItemsMatched;
            EventManager.OnLevelWin  -= HandleLevelEnded;
            EventManager.OnLevelLose -= HandleLevelEnded;
        }
        #endregion

        #region INITIALIZE
        // Pha 1: chỉ dựng state của MÌNH từ level, KHÔNG đọc controller khác.
        public override void Initialized(LevelInfo levelInfo)
        {
            base.Initialized(levelInfo);
            _state = 0;
            IsActive = false;
        }
        // Pha 2: được phép đọc chéo qua _gamePlayController (mọi con đã init xong).
        public override void PostInitialized()
        {
            base.PostInitialized();
            // vd: _gamePlayController.BoardController.TryGetBoardBounds(out var b);
        }
        #endregion

        #region EVENT METHODS
        private void HandleItemsMatched(Cell cell, ItemType type) { }
        private void HandleLevelEnded() { }   // dọn state khi win/lose
        #endregion

        #region PRIVATE METHODS
        #endregion
    }
}
```

**Wire vào Root (bắt buộc, nếu quên → follower im lặng không chạy):**
```csharp
// trong RootController:
[SerializeField] private XxxController xxxController;      // + kéo ref trong Inspector
// Initialized():     xxxController.Initialized(level);
// PostInitialized():  xxxController.PostInitialized();
```

Quy tắc riêng:
- Cần `_gamePlayController` sẵn ngay khi Root xuất hiện (hiếm) → override `OnControllerReady`, **nhớ gọi `base.OnControllerReady(controller)`** để không mất cache ref.
- Follower đọc controller khác thì đi qua **property facade của Root** (`_gamePlayController.BoardController`…), không giữ ref chéo trực tiếp.

---

## Archetype 3 — Sub-follower + Hub

Khi có nhiều biến thể cùng họ (booster, enemy, tile-effect…). Một **Follower làm Hub** (vd `BoosterController`) route theo type; các con kế thừa 1 abstract base (vd `BaseBoosterController`) và được Hub tiêm ref.

**Abstract base cho con** (mẫu `BaseBoosterController`):
```csharp
public abstract class BaseXxxController : BaseBehaviour
{
    public abstract XxxType Type { get; }
    protected GamePlayController GamePlayController { get; private set; }
    protected XxxHubController _hub;

    public void Init(XxxHubController hub, GamePlayController gamePlay)
    { _hub = hub; GamePlayController = gamePlay; }        // Hub tiêm ref, con không tự Find

    public virtual void Initialized(LevelInfo level) { }
    public virtual void PostInitialized() { }
    public abstract void Activate();

    protected void NotifyStarted() => _hub?.HandleStarted(Type);
    protected void NotifyEnded()   => _hub?.HandleEnded(Type);
}
```

**Hub (là 1 Follower) — điểm phải sửa khi thêm biến thể:**
```csharp
public override void Initialized(LevelInfo level)
{
    base.Initialized(level);
    xxxChild.Init(this, _gamePlayController);     // tiêm ref
    xxxChild.Initialized(level);                  // Hub tự fan-out xuống con
}
protected override void OnEnable()  { base.OnEnable();  EventManager.UseXxx += HandleUse; }
private void HandleUse(XxxType type)
{
    switch (type) { case XxxType.Abc: xxxChild.Activate(); break; }   // route theo type
}
```

> Thêm 1 biến thể = tạo class kế thừa base + thêm `case` route + serialize ref + gọi `Init/Initialized` trong Hub. Nếu số biến thể lớn, cân nhắc `Dictionary<Type, BaseXxxController>` để khỏi sửa `switch` mỗi lần (xem rules.md — API tái sử dụng).

---

## Archetype 4 — POCO logic (không MonoBehaviour)

Logic thuần, đời sống gắn 1 **Coordinator** do Root sở hữu (mẫu `CellMovementCoordinator` + `IMoveController`). Không có Inspector, không hook Unity — Coordinator gọi vòng đời tường minh và có thể truyền event.

```csharp
public interface IXxxController
{
    void Build(/* input rõ ràng */);
    void Play();
    void Stop();
}

// Coordinator (POCO, Root new lên và giữ):
public class XxxCoordinator
{
    private readonly List<IXxxController> _controllers = new() { new AbcController(), new DefController() };
    public void Build(...) { foreach (var c in _controllers) c.Build(...); }
    public void Play()     { foreach (var c in _controllers) c.Play(); }
    public void Stop()     { foreach (var c in _controllers) c.Stop(); }
}
```

Root sở hữu coordinator và điều khiển theo game state (mẫu `GamePlayController._movement`): `Stop()` trong `Initialized` (dừng level cũ), `Build()+Play()` khi `OnGameStart`, `Stop()` khi win/lose.

---

## Giao tiếp: ref trực tiếp hay event bus?

| Tình huống | Kênh |
|-----------|------|
| Follower cần đọc state/API controller khác | **Ref qua Root facade** (`_gamePlayController.XxxController`) |
| Follower báo "đã xảy ra chuyện gì" cho ≥1 bên quan tâm | **Event bus** `EventManager.OnXxx?.Invoke(...)` |
| Yêu cầu 1 hành động không rõ ai xử lý | **Event bus** dạng mệnh lệnh (`UseBooster`, `PlaySfx`) |
| Kết thúc level | **Gọi ngược Root** (`CheckWin/LoseCondition`), Root mới raise event |

Nguyên tắc: **con không gọi thẳng con** (tránh coupling chéo). Ref chỉ đi theo trục Root↔con; ngang hàng thì qua event. Thêm event mới theo đúng quy ước `EventManager.<Feature>.cs` (xem `Toppic/CLAUDE.md`): field `public static Action`, publish bằng `?.Invoke`, subscribe/unsubscribe đối xứng OnEnable/OnDisable.

## Async & token lifecycle

- Mọi vòng lặp/`UniTask` link vào **`CurToken`** của `BaseBehaviour` → tự hủy khi `OnStartLoadingPhase0` (chuyển scene).
- `try { await ... CurToken } catch (OperationCanceledException) { return; }` — thoát êm khi scene đổi.
- Tác vụ có thể bị hủy sớm (booster đang chạy, timer) → dùng `CancellationTokenSource.CreateLinkedTokenSource(CurToken)` + `finally` khôi phục state (mẫu `FreezeBoosterController.FreezeAsync`).
- Cần thời gian thực bất chấp làm-chậm-đồng-hồ → `DelayType.UnscaledDeltaTime` (không đụng `Time.timeScale`).

## Checklist trước khi coi là xong

- [ ] Chọn đúng 1 trong 4 archetype; kế thừa đúng base class.
- [ ] (Follower) Root đã có `[SerializeField]` ref + gọi `Initialized`/`PostInitialized` đúng pha; đã kéo ref trong Inspector/prefab.
- [ ] (Sub-follower) Hub đã `Init()` tiêm ref + fan-out `Initialized` + thêm `case` route.
- [ ] Event wire trong `OnEnable`, gỡ trong `OnDisable`, **có gọi `base.OnEnable/OnDisable`**.
- [ ] `Initialized` không đọc controller khác; đọc chéo để ở `PostInitialized`.
- [ ] Giao tiếp chéo qua event/Root facade, không gọi thẳng con↔con.
- [ ] Async link `CurToken`; state khôi phục trong `finally`; xử lý win/lose (dọn/hủy).
- [ ] Kết thúc level chỉ qua Root; không tự raise `OnLevelWin/Lose`.
- [ ] Region/field theo `.claude/rules.md`; không LINQ hot path; không null-check thừa ref serialized.

## Cạm bẫy thường gặp

- **Follower không chạy gì cả** → quên wire vào Root (thêm ref + gọi Initialized). Đây là lỗi #1.
- **NRE khi đọc controller khác trong `Initialized`** → phải chuyển sang `PostInitialized` (pha 1 chưa chắc con kia xong).
- **Override `OnControllerReady`/`OnEnable`/`OnDisable` mà quên `base.…`** → mất cache ref hoặc mất hook token.
- **Rebuild trùng do event lặp** → hành động nặng trên event có thể bắn nhiều lần (vd `OnGameStart` bị `FreezeBooster` bắn lại) nên để idempotent hoặc guard.
- **Booster/effect chạy ở level chưa bật hệ liên quan** (vd Freeze khi timer disabled level 1) → cân nhắc guard điều kiện trước khi `Activate`.

## File tham chiếu (ví dụ thật)

- Base khung: `Toppic/Base/BaseGameManager.cs`, `BaseGameController.cs`, `StateGameFollower.cs`, `BaseBehaviour.cs`; `Base/StateGamePlayFollower.cs`; `Toppic/Other/DefaultExecutionOrderValue.cs`.
- Root: `Game/GamePlayController.cs` (facade + trọng tài kết thúc + sở hữu coordinator).
- Follower: `Game/Timer/GameTimerController.cs`, `Game/Combo/ComboController.cs`, `Game/Input/BoardInputController.cs`.
- Sub-follower + Hub: `Game/Booster/BaseBoosterController.cs` + `BoosterController.cs` + `FreezeBoosterController.cs`.
- POCO + Coordinator: `Game/Movement/CellMovementCoordinator.cs` + `IMoveController.cs` + `DirectionalMoveController.cs`.
- Event bus: `Toppic/CLAUDE.md` (quy ước), `Game/EventManager.Gameplay.cs`, `Game/Booster/EventManager.Booster.cs`.
