#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from apply_weak_model_response import apply_response_to_text, load_schema, make_rename_map, parse_frontmatter
from kb_paths import repo_root, resolve_vault_path


DERIVATION_FIXES: dict[str, str] = {
    "吸引子": "對自治系統 $\\dot{\\mathbf{x}}=\\mathbf{f}(\\mathbf{x})$，先找固定點 $\\mathbf{f}(\\mathbf{x}_*)=0$。在線性化下令 $\\delta\\dot{\\mathbf{x}}=J(\\mathbf{x}_*)\\delta\\mathbf{x}$，若 Jacobian 的特徵值滿足 $\\Re\\lambda_i<0$，則 $\\delta\\mathbf{x}(t)\\sim e^{\\lambda_i t}$ 衰減，鄰近軌道收斂到 $\\mathbf{x}_*$。極限環與奇異吸引子則是這個穩定收斂概念在非線性不變集合上的延伸。",
    "混沌": "從 $\\dot{\\mathbf{x}}=\\mathbf{f}(\\mathbf{x})$ 對兩條鄰近軌道做變分，可得 $\\delta\\dot{\\mathbf{x}}=D\\mathbf{f}(\\mathbf{x})\\delta\\mathbf{x}$。若解滿足 $\\|\\delta\\mathbf{x}(t)\\|\\approx \\|\\delta\\mathbf{x}(0)\\|e^{\\lambda t}$ 且最大李雅普諾夫指數 $\\lambda>0$，微小初值誤差會被指數放大。這就把確定性方程推到長期不可預測：方程沒變隨機，但相空間中鄰近點的分離速度太快。",
    "相圖": "對二維自治系統 $\\dot{x}=f(x,y),\\ \\dot{y}=g(x,y)$，消去時間可得軌道斜率 $\\frac{dy}{dx}=\\frac{g(x,y)}{f(x,y)}$。這一步把運動方程轉成相平面上的幾何流線；再由 $f=g=0$ 找固定點，並以 Jacobian 判斷穩定性，就能從局部斜率場推出整體流向、極限環與分離曲線。",
    "LC電路": "對理想 LC 迴路套用 Kirchhoff 電壓定律，得 $V_L+V_C=0$。用 $V_L=L\\,\\frac{dI}{dt}$、$V_C=\\frac{q}{C}$ 且 $I=\\frac{dq}{dt}$ 代入，可得 $L\\frac{d^2 q}{dt^2}+\\frac{1}{C}q=0$。這就是簡諧振盪方程，因此角頻率為 $\\omega=1/\\sqrt{LC}$，電荷與電流在電容電場能和電感磁場能間週期交換。",
    "真空電容率": "在 Maxwell 方程組中，真空波速由 $c^2=\\frac{1}{\\mu_0\\epsilon_0}$ 決定，因此 $\\epsilon_0=\\frac{1}{\\mu_0 c^2}$。這說明 $\\epsilon_0$ 不是孤立常數，而是把靜電作用尺度與電磁波傳播速度接在一起的量。把它代回庫侖定律 $F=\\frac{1}{4\\pi\\epsilon_0}\\frac{q_1q_2}{r^2}$，就能看到真空對電場強度的允許程度如何設定相互作用大小。",
    "電容率": "介質中若極化與外電場近似線性，則有 $\\mathbf{P}=\\epsilon_0\\chi_e\\mathbf{E}$。位移場定義為 $\\mathbf{D}=\\epsilon_0\\mathbf{E}+\\mathbf{P}$，代入得 $\\mathbf{D}=\\epsilon_0(1+\\chi_e)\\mathbf{E}\\equiv \\epsilon\\mathbf{E}$。因此 $\\epsilon=\\epsilon_r\\epsilon_0$，它是從極化響應推出的有效比例常數，而不是額外硬塞進去的符號。",
    "電磁鐵": "把線圈近似為長螺線管，對包圍線圈的安培迴路用 $\\oint \\mathbf{B}\\cdot d\\mathbf{l}=\\mu n I\\,l$，可得管內近似均勻磁場 $B\\approx \\mu n I$。若再加入鐵芯，材料磁導率 $\\mu$ 顯著增加，同樣電流就能得到更強磁場。電磁鐵的工作原理因此可視為安培環路定律加上高磁導材料放大磁通。",
    "電路": "把電荷守恆套到任一節點，流入與流出電流必須平衡，故 $\\sum I_{\\text{in}}=\\sum I_{\\text{out}}$，這就是 Kirchhoff 電流定律。再對閉合迴路做能量守恆，得到 $\\sum \\Delta V=0$，即 Kirchhoff 電壓定律。整個電路分析就是把元件關係如 $V=IR$、$V=L\\,dI/dt$、$q=CV$ 代入這兩條守恆式。",
    "偏微分方程": "若一個守恆量密度為 $u(\\mathbf{x},t)$、通量為 $\\mathbf{J}$、源項為 $s$，對體積 $V$ 有 $\\frac{d}{dt}\\int_V u\\,dV=-\\oint_{\\partial V}\\mathbf{J}\\cdot d\\mathbf{A}+\\int_V s\\,dV$。用高斯定理轉成局部形式，就得 $\\frac{\\partial u}{\\partial t}+\\nabla\\cdot \\mathbf{J}=s$。這一步就是偏微分方程在物理中的來源：把整體守恆律壓縮成每一點都必須滿足的局部關係。",
    "參考系": "若兩慣性系以速度 $v$ 沿 $x$ 方向相對運動，Galilean 變換給出 $x'=x-vt,\\ t'=t$。對時間微分可得 $u'_x=u_x-v$，再微分一次得 $a'_x=a_x$。因此在牛頓力學裡，運動方程形式在不同慣性參考系下保持一致；參考系改變的是座標與速度表達，不是物理定律本身。",
    "場": "若作用不再寫成兩粒子直接超距拉扯，而是先定義每點的勢函數 $\\phi(\\mathbf{r})$，則力可由梯度推出：$\\mathbf{E}(\\mathbf{r})=-\\nabla \\phi(\\mathbf{r})$，進一步對電荷 $q$ 有 $\\mathbf{F}=q\\mathbf{E}$。也就是說，場的數學生成方式是先在時空每點指定一個量，再由空間變化率或局部值推出可觀測作用。",
    "對稱性": "設變換 $q_i\\to q_i+\\varepsilon\\delta q_i$ 不改變作用量，即 $\\delta S=0$。對 $S=\\int L(q,\\dot q,t)\\,dt$ 做變分並用 Euler-Lagrange 方程，可得 $\\frac{d}{dt}\\!\\left(\\sum_i \\frac{\\partial L}{\\partial \\dot q_i}\\delta q_i\\right)=0$。因此括號中的量守恆。這就是從對稱性推出守恆量的數學核心，也是 Noether 思想最直接的推導框架。",
    "慣性": "若合力為零，牛頓第二定律寫成 $\\frac{d\\mathbf{p}}{dt}=0$。對質量固定的情況有 $\\mathbf{p}=m\\mathbf{v}$，因此 $m\\frac{d\\mathbf{v}}{dt}=0 \\Rightarrow \\frac{d\\mathbf{v}}{dt}=0$。所以物體會維持靜止或等速直線運動。慣性不是額外加上的神祕力，而是無外力時動量不變這條守恆式在運動學上的直接表現。",
    "暫態": "對線性系統 $\\dot{x}=Ax+b$，一般解可寫成 $x(t)=x_{\\mathrm{ss}}+e^{At}\\!\\bigl(x(0)-x_{\\mathrm{ss}}\\bigr)$，其中 $Ax_{\\mathrm{ss}}+b=0$。後面的 $e^{At}$ 項就是暫態：它攜帶初始條件資訊，並在系統穩定時隨時間衰減。暫態因此不是另一種定律，而是完整解中那個會消失、卻決定系統如何靠近長時間行為的部分。",
    "穩態": "穩態從動力方程的時間不變條件推出。若 $\\dot{x}=Ax+b$，令 $\\dot{x}=0$ 即得 $Ax_{\\mathrm{ss}}+b=0$。對可逆矩陣 $A$，有 $x_{\\mathrm{ss}}=-A^{-1}b$。也就是說，穩態不是不動的口語說法，而是把演化方程中的時間導數壓成零後得到的平衡解；對交流驅動系統則對應到固定頻率、固定振幅的長時間特解。",
    "邊界條件": "微分方程先給出一族一般解，邊界條件再把常數定掉。以一維 Laplace 方程 $\\frac{d^2u}{dx^2}=0$ 為例，一般解是 $u(x)=Ax+B$；若要求 $u(0)=u_0,\\ u(L)=u_L$，則 $B=u_0,\\ A=\\frac{u_L-u_0}{L}$。所以邊界條件的角色不是附註，而是把所有數學可能壓縮成符合實際邊界的唯一物理解。",
    "拉格朗日乘數法": "要在約束 $g(\\mathbf{x})=0$ 下極值化 $f(\\mathbf{x})$，令輔助函數 $\\mathcal{L}(\\mathbf{x},\\lambda)=f(\\mathbf{x})-\\lambda g(\\mathbf{x})$。對各變數與 $\\lambda$ 取偏導並令其為零，可得 $\\nabla f=\\lambda \\nabla g,\\ g(\\mathbf{x})=0$。這表示在極值點，目標函數的最陡上升方向必須與約束面法向平行；否則還能沿約束面切向再改進，極值就不成立。",
    "非完整系統": "若速度約束寫成 $\\sum_i a_i(q,t)\\,\\dot q_i + a_0(q,t)=0$，而它不能積分成單純的 $F(q,t)=0$，系統就是非完整的。關鍵在於約束直接作用於速度空間，而不是只限制可達位置集合；因此變分時不能把它當成普通座標約束直接代入，而要用乘數或 d'Alembert-Lagrange 形式把虛位移限制一起帶入。",
    "局域性": "在局域場論中，作用量通常寫成 $S=\\int \\mathcal{L}\\bigl(\\phi(x),\\partial_\\mu \\phi(x)\\bigr)\\,d^4x$。對 $\\phi$ 變分得到 Euler-Lagrange 方程 $\\partial_\\mu\\!\\left(\\frac{\\partial \\mathcal{L}}{\\partial(\\partial_\\mu\\phi)}\\right)-\\frac{\\partial \\mathcal{L}}{\\partial\\phi}=0$。整個方程只依賴同一時空點 $x$ 的場值與鄰近導數，這就是局域性的數學內容：動力學由局部資料決定，而不是瞬時讀取遠方任意點。",
    "連續譜": "自由粒子的定態薛丁格方程為 $-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi}{dx^2}=E\\psi$。其解為 $\\psi(x)=Ae^{ikx}+Be^{-ikx}$，且 $E=\\frac{\\hbar^2 k^2}{2m}$。因為 $k$ 不再受束縛邊界條件量子化，可以連續取值，所以 $E$ 也形成連續譜。換句話說，連續譜是沒有把波函數鎖進有限邊界後自然出現的本徵值結構。",
    "量子化": "量子化最直觀的來源是邊界條件。以無限深方井 $0<x<L$ 為例，薛丁格方程解可寫為 $\\psi(x)=A\\sin kx+B\\cos kx$；由 $\\psi(0)=\\psi(L)=0$ 得 $k_n=\\frac{n\\pi}{L}$。因此能量只能取 $E_n=\\frac{\\hbar^2 k_n^2}{2m}=\\frac{n^2\\pi^2\\hbar^2}{2mL^2}$。離散值不是憑空規定，而是波動方程配上可接受邊界後的結果。",
    "不可逆過程": "不可逆性的數學標記是熵產生。把熵變分成交換與內生兩部分，可寫成 $dS=\\frac{\\delta Q}{T}+d_iS,\\ d_iS>0$。只要存在有限溫差、黏滯、摩擦或擴散，系統內部就會產生正的 $d_iS$，因此即使把外界條件反向，整條路徑也無法原樣倒回。這就是不可逆過程從熱力學第二定律落到計算式的方式。",
    "可逆過程": "可逆過程是把真實演化推到無限慢、無耗散的極限，此時內部熵產生為零：$d_iS=0$。因此熵變只剩交換項 $dS=\\frac{\\delta Q_{\\mathrm{rev}}}{T}$。這條式子反過來也說明了可逆過程的重要性：它提供一條可積分的理想路徑，讓熵成為狀態函數；真實過程未必可逆，但計算狀態差時可以借用這條極限路徑。",
    "熱力學": "把熱與功都視為內能的交換方式，第一定律寫成 $dU=\\delta Q-\\delta W$。若只有準靜態體積功，$\\delta W=P\\,dV$；再用可逆熱量關係 $\\delta Q=T\\,dS$，就得到 $dU=T\\,dS-P\\,dV$。這一步把熱力學從口語上的熱與功守恆推成可以微分計算的狀態方程框架。",
    "統計物理": "從微觀態能量 $E_i$ 與熱浴溫度 $T$ 出發，平衡分布由 Boltzmann 因子給出：$p_i=\\frac{e^{-\\beta E_i}}{Z},\\ Z=\\sum_i e^{-\\beta E_i},\\ \\beta=\\frac{1}{k_BT}$。一旦配分函數 $Z$ 決定，內能便可由 $U=\\sum_i p_iE_i=-\\frac{\\partial \\ln Z}{\\partial \\beta}$ 推出。這就是統計物理把巨觀熱量學量從大量微觀態平均出來的核心推導。",
    "光線模型": "當波長遠小於系統尺度時，波前局部可視為平面，光線便定義為波前法線。更正式地，Fermat 原理要求實際路徑使光程 $\\delta\\!\\int n\\,ds=0$。對均勻介質這會退化成直線傳播；在分段介質上則推出反射與折射定律。也就是說，光線模型不是否定波，而是把波動方程壓到短波長極限後得到的幾何近似。",
    "入射角": "設入射光方向為 $\\mathbf{k}_i$、界面法線為 $\\mathbf{n}$，入射角由兩者夾角定義：$\\cos\\theta_i=\\frac{\\mathbf{k}_i\\cdot \\mathbf{n}}{\\|\\mathbf{k}_i\\|\\,\\|\\mathbf{n}\\|}$。這個定義不是純記號遊戲，而是把相對於界面的方向轉成相對於法線的角度，好讓反射與折射條件只需比較垂直與平行分量。",
    "反射": "把入射波向量分解為法線與切向分量，界面上切向分量必須連續，因此反射只會翻轉法線分量：$\\mathbf{k}_r=\\mathbf{k}_i-2(\\mathbf{k}_i\\cdot \\hat{\\mathbf{n}})\\hat{\\mathbf{n}}$。由此立刻得到法線兩側夾角相等，即 $\\theta_r=\\theta_i$。所以反射的推導本質上是分量分解加上界面幾何條件，而不是單純背誦一條定律。",
    "反射角": "若入射方向為 $\\mathbf{k}_i$、反射方向為 $\\mathbf{k}_r$、法線為 $\\hat{\\mathbf{n}}$，反射可寫成 $\\mathbf{k}_r=\\mathbf{k}_i-2(\\mathbf{k}_i\\cdot \\hat{\\mathbf{n}})\\hat{\\mathbf{n}}$。這表示切向分量不變、法向分量反號，因此反射光與法線的夾角滿足 $\\theta_r=\\theta_i$。反射角其實就是這個向量分解結論的角度版本。",
    "平面鏡成像": "由反射定律 $\\theta_i=\\theta_r$，取物點、鏡面與視線形成的兩個三角形，可得它們在鏡面兩側互為全等，因此像點到鏡面的距離與物點到鏡面的距離相等：$d_i=d_o$。這一步說明平面鏡像不是鏡後真的有物體，而是所有反射光線的反向延長線交於同一虛點。",
    "惠更斯原理": "設某時刻波前為一條等相位面，經過短時間 $\\Delta t$ 後，波前上每一點都向外發出半徑 $v\\Delta t$ 的次級波。新波前就是這些小球面的包絡面。若用幾何語言寫，傳播距離滿足 $\\Delta s=v\\Delta t$；把包絡面在界面處拼接，就能推出反射與折射時的角度關係。",
    "折射率量測實驗": "量測時先記錄入射角 $\\theta_i$ 與折射角 $\\theta_t$，再套用 Snell 定律 $n_1\\sin\\theta_i=n_2\\sin\\theta_t$。若空氣近似 $n_1\\approx 1$，則待測介質折射率為 $n\\approx \\frac{\\sin\\theta_i}{\\sin\\theta_t}$。因此實驗推導的核心不是直接看見折射率，而是把可量的角度透過界面匹配條件反推出材料常數。",
    "折射角": "由界面上相位連續或切向波數守恆，可得 $n_1\\sin\\theta_i=n_2\\sin\\theta_t$。因此折射角滿足 $\\sin\\theta_t=\\frac{n_1}{n_2}\\sin\\theta_i$。這表示折射角不是獨立量，而是入射角與兩側介質折射率共同決定的結果；介質越慢，光線越向法線偏折。",
    "相位": "對簡諧波 $A\\cos(kx-\\omega t+\\phi_0)$，括號內的 $\\phi(x,t)=kx-\\omega t+\\phi_0$ 就是相位。它的推導來自把波形寫成振幅乘週期函數，並把空間平移與時間演化都壓進同一個角變數。兩個波是否同調、何時相長或相消，最後都化成比較 $\\Delta\\phi$ 是否固定以及是否等於 $2m\\pi$ 或 $(2m+1)\\pi$。",
    "相干性": "若兩個場的時間相關函數定義為 $G^{(1)}(\\tau)=\\langle E^*(t)E(t+\\tau)\\rangle$，則歸一化後 $g^{(1)}(\\tau)=\\frac{G^{(1)}(\\tau)}{G^{(1)}(0)}$。當 $|g^{(1)}(\\tau)|\\approx 1$ 時，相位關係在時間延遲 $\\tau$ 下仍穩定，干涉條紋就清楚；若它快速衰減到 0，相位記憶消失，干涉也會洗掉。這就是相干性的推導核心。",
    "向量": "選定一組基底 $\\{\\mathbf{e}_i\\}$ 後，任何向量都可展開為 $\\mathbf{v}=\\sum_i v_i\\mathbf{e}_i$。內積則由 $\\mathbf{v}\\cdot\\mathbf{w}=\\sum_i v_iw_i$ 給出，於是長度與投影都能從分量算出。這個推導告訴你：向量不是箭頭圖像而已，它本質上是對基底可線性分解，且能透過分量做幾何運算的對象。",
    "張量": "二階張量可看成把兩個向量槽位線性地映到數值或另一向量的對象。若座標變換矩陣為 $a_{ij}$，則分量必須依規則 $T'_{ij}=a_{ik}a_{jl}T_{kl}$ 變換，這樣像 $T_{ij}x_i y_j$ 這類物理量才在換座標後保持不變。張量的推導就在這裡：它是為了保住物理關係的座標不變性而被迫引入的。",
    "機率與統計": "離散分布先滿足正規化 $\\sum_i p_i=1$。在此基礎上，平均值與變異數分別定義為 $\\mu=\\sum_i x_i p_i,\\ \\sigma^2=\\sum_i (x_i-\\mu)^2p_i=\\langle x^2\\rangle-\\langle x\\rangle^2$。這一步把不確定轉成可計算量：不是只說結果會波動，而是用分布權重把中心趨勢與散布程度都從同一套機率語言推出。",
    "矩陣": "把線性映射 $A$ 作用在基底向量 $\\mathbf{e}_j$ 上，可寫成 $A\\mathbf{e}_j=\\sum_i A_{ij}\\mathbf{e}_i$，因此任意向量 $\\mathbf{x}$ 的像就是 $\\mathbf{y}=A\\mathbf{x}$。若要找哪些方向只被伸縮不被旋轉，令 $A\\mathbf{v}=\\lambda \\mathbf{v}$，便得到特徵值條件 $\\det(A-\\lambda I)=0$。矩陣因此是把線性關係與耦合結構壓縮成單一算子的工具。",
    "群論基礎": "若一組變換在組合下封閉，且滿足結合律、單位元與反元素，便構成群。用運算符表示就是：對任意 $g_1,g_2\\in G$，有 $U(g_1)U(g_2)=U(g_1g_2),\\ U(e)=I,\\ U(g^{-1})=U(g)^{-1}$。這個推導重點不是公式本身，而是說明對稱操作可以被一致地連乘與反轉，因此才能系統性地分析守恆量與表示理論。",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_blocked_tasks(report_path: Path, task_dir: Path) -> list[tuple[dict, Path]]:
    report = load_json(report_path)
    blocked_names = [item["task"] for item in report.get("skipped", []) if item.get("reason") == "blocked"]
    results: list[tuple[dict, Path]] = []
    for name in blocked_names:
        task_path = task_dir / name
        task = load_json(task_path)
        results.append((task, task_path))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill blocked derivation tasks with curated content.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--report", default="tmp/derivation_repair_apply_dryrun.json", help="Blocked report JSON path")
    parser.add_argument("--task-dir", default="batch_tasks/stronger_model/derivation_repair", help="Derivation task directory")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back to the vault")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    report_path = (repo / args.report).resolve()
    task_dir = (repo / args.task_dir).resolve()
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    schema = load_schema(schema_dir)

    blocked_tasks = collect_blocked_tasks(report_path, task_dir)
    if not blocked_tasks:
        raise SystemExit("No blocked derivation tasks found.")

    changed = 0
    missing_titles: list[str] = []

    for task, _task_path in blocked_tasks:
        title = str(task["source_context"]["title"]).strip()
        replacement = DERIVATION_FIXES.get(title)
        if not replacement:
            missing_titles.append(title)
            continue

        note_path = (vault / str(task["note_path"])).resolve()
        text = note_path.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(text)
        note_type = str(frontmatter.get("type", "")).strip()
        if note_type != str(task.get("note_type", "")).strip():
            raise SystemExit(f"Task note_type mismatch for {note_path}: {task.get('note_type')!r} != {note_type!r}")

        rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
        rename_map = make_rename_map(rename_rules)
        updated_text, _matched_heading = apply_response_to_text(
            text,
            note_type=note_type,
            target_section=str(task["target_section"]),
            replacement_body=replacement,
            rename_map=rename_map,
        )
        if updated_text != text:
            changed += 1
            if args.write:
                note_path.write_text(updated_text, encoding="utf-8")

    if missing_titles:
        raise SystemExit(f"Missing derivation fixes for: {', '.join(missing_titles)}")

    print("Blocked derivation fill summary")
    print(f"- report: {report_path}")
    print(f"- task dir: {task_dir}")
    print(f"- vault: {vault}")
    print(f"- blocked tasks: {len(blocked_tasks)}")
    print(f"- changed: {changed}")
    print(f"- write: {args.write}")


if __name__ == "__main__":
    main()
