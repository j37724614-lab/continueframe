import math                                                            #引入 Python 內建的數學模組。
import matplotlib.pyplot as plt                                        #引入 Matplotlib 的繪圖介面模組
import matplotlib.animation as animation                               #引入 Matplotlib 的動畫模組，用來製作逐幀更新的動畫。

# === 幾何函式 ===
def unit(v):  # 將向量 v 轉換成單位向量（長度為 1）
    x, y = v
    n = math.hypot(x, y)  # 計算平方根(x² + y²)
    return (x/n, y/n) if n > 0 else (0.0, -1.0)

def rot(v, ang_rad):  # 對向量 v 旋轉 ang_rad 弧度
    x, y = v
    c, s = math.cos(ang_rad), math.sin(ang_rad)
    return (x*c - y*s, x*s + y*c)  # 二維旋轉公式

def angle_between_points(p_center, p1, p2):  # 計算三點構成的夾角
    v1 = (p1[0]-p_center[0], p1[1]-p_center[1])
    v2 = (p2[0]-p_center[0], p2[1]-p_center[1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]  # 內積
    m1, m2 = math.hypot(*v1), math.hypot(*v2)
    if m1 == 0 or m2 == 0:
        return 0.0
    cos_t = max(-1.0, min(1.0, dot/(m1*m2)))  # 避免浮點誤差
    return math.degrees(math.acos(cos_t))  # 以角度回傳夾角

# === 四輸入 → 八關節 ===
def synth_pose_four_inputs(theta_L, theta_R, dist_L, dist_R,
                           center=(320, 260), shoulder_width=75, hip_width=75,
                           torso_len=130, upper_arm=65, forearm=80):
    cx, cy = center  # 軀幹中心
    trunk_dir = (0.0, -1.0)  # 軀幹朝下方向

    # 定義軀幹四個節點：肩與髖
    p0 = (cx - shoulder_width/2, cy)           # 右肩
    p1 = (cx + shoulder_width/2, cy)           # 左肩
    p2 = (cx - hip_width/2, cy - torso_len)    # 右髖
    p3 = (cx + hip_width/2, cy - torso_len)    # 左髖

    # 根據輸入角度計算手臂方向
    arm_dir_R = unit(rot(trunk_dir, -math.radians(theta_R)))  # 右上臂方向
    arm_dir_L = unit(rot(trunk_dir,  math.radians(theta_L)))  # 左上臂方向

    # 根據上臂長計算肘部位置
    p4 = (p0[0] + arm_dir_R[0]*upper_arm, p0[1] + arm_dir_R[1]*upper_arm)  # 右肘
    p5 = (p1[0] + arm_dir_L[0]*upper_arm, p1[1] + arm_dir_L[1]*upper_arm)  # 左肘

    # 根據垂直距離與前臂長計算手腕位置
    wy_R = p0[1] - dist_R
    dx_R = math.sqrt(max(0.0, forearm**2 - (wy_R - p4[1])**2))
    wx_R = p4[0] + math.copysign(dx_R, arm_dir_R[0])
    p6 = (wx_R, wy_R)

    wy_L = p1[1] - dist_L
    dx_L = math.sqrt(max(0.0, forearm**2 - (wy_L - p5[1])**2))
    wx_L = p5[0] + math.copysign(dx_L, arm_dir_L[0])
    p7 = (wx_L, wy_L)

    return [p0,p1,p2,p3,p4,p5,p6,p7]

# === 輸入多組資料 ===
theta_L_list = [110, 115, 120, 125, 130, 135]
theta_R_list = [170, 165, 160, 155, 150, 145]
dist_L_list  = [80, 75, 70, 65, 60, 55]
dist_R_list  = [90, 85, 80, 75, 70, 65]

# === 視覺化設定 ===
connections = [(0,1),(0,4),(4,6),(1,5),(5,7),(0,2),(1,3),(2,3)]
fig, ax = plt.subplots(figsize=(7,7))
ax.set_xlim(0, 500)
ax.set_ylim(0, 500)
ax.set_xticks(range(0, 501, 100))
ax.set_yticks(range(0, 501, 100))
ax.set_aspect('equal', adjustable='box')
ax.grid(True)
ax.set_xlabel('x (每格 = 100)')
ax.set_ylabel('y (每格 = 100)')

# 建立繪圖元件
lines = [ax.plot([], [], 'orange', lw=2)[0] for _ in connections]
points = ax.scatter([], [], color='blue', s=60)
vline_R, = ax.plot([], [], '--', color='purple', lw=2)
vline_L, = ax.plot([], [], '--', color='green', lw=2)
hline, = ax.plot([], [], '--', color='gray', lw=1.5)
text_title = ax.text(20, 470, "", fontsize=11, color='darkred')
dist_text_R = ax.text(400, 450, "", fontsize=9, color='purple')
dist_text_L = ax.text(400, 430, "", fontsize=9, color='green')

# === 更新每一幀 ===
def update(frame):
    thL = theta_L_list[frame]
    thR = theta_R_list[frame]
    dL  = dist_L_list[frame]
    dR  = dist_R_list[frame]
    pts = synth_pose_four_inputs(thL, thR, dL, dR)
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]

    for i, (a,b) in enumerate(connections):
        lines[i].set_data([x[a],x[b]],[y[a],y[b]])
    points.set_offsets(list(zip(x,y)))

    # 更新垂直距離線與肩線
    vline_R.set_data([pts[6][0], pts[6][0]], [min(pts[6][1], pts[0][1]), max(pts[6][1], pts[0][1])])
    vline_L.set_data([pts[7][0], pts[7][0]], [min(pts[7][1], pts[1][1]), max(pts[7][1], pts[1][1])])
    y_mid = (pts[0][1] + pts[1][1]) / 2
    hline.set_data([0, 500], [y_mid, y_mid])

    # 更新文字
    dy_right = abs(pts[6][1] - pts[0][1])
    dy_left  = abs(pts[7][1] - pts[1][1])
    text_title.set_text(f"Frame {frame+1}: θR={thR}°, θL={thL}°, dR={dR}, dL={dL}")
    dist_text_R.set_text(f"右腕距離: {dy_right:.1f}")
    dist_text_L.set_text(f"左腕距離: {dy_left:.1f}")

    return lines + [points, vline_R, vline_L, hline, text_title, dist_text_R, dist_text_L]

# === 動畫生成 ===
num_frames = min(len(theta_L_list), len(theta_R_list), len(dist_L_list), len(dist_R_list))
ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=600, blit=True)

# 顯示動畫（VSCode會開啟外部視窗顯示）
plt.show()

# 另存為 mp4
ani.save("skeleton_sequence.mp4", writer="ffmpeg", fps=2)
print("✅ 動畫已輸出完成：skeleton_sequence.mp4")
