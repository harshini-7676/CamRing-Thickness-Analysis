import cv2
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# ===============================
# 1️⃣ Load Image
# ===============================
image_path = "cam.jpg"

img = cv2.imread(image_path)

if img is None:
    print("❌ ERROR: Image not found. Check file name.")
    exit()

# Resize for consistency
img = cv2.resize(img, (800, 800))

# Create output folder if not exists
os.makedirs("output", exist_ok=True)

# ===============================
# 2️⃣ Convert to Gray + Blur
# ===============================
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# ===============================
# 3️⃣ Edge Detection
# ===============================
edges = cv2.Canny(blur, 50, 150)

cv2.imwrite("output/edges.jpg", edges)

# ===============================
# 4️⃣ Get Center (FIXED VERSION)
# ===============================
height, width = img.shape[:2]
center_x = width // 2
center_y = height // 2

print("Center:", center_x, center_y)

# ===============================
# 5️⃣ Measure Thickness
# ===============================
angles = np.arange(0, 360, 5)

outer_radii = []
inner_radii = []

for angle in angles:
    theta = np.deg2rad(angle)
    
    for r in range(10, 400):
        x = int(center_x + r * np.cos(theta))
        y = int(center_y + r * np.sin(theta))

        if 0 <= x < width and 0 <= y < height:
            if edges[y, x] == 255:
                outer_radii.append(r)
                break

    for r in range(10, 400):
        x = int(center_x + r * np.cos(theta))
        y = int(center_y + r * np.sin(theta))

        if 0 <= x < width and 0 <= y < height:
            if edges[y, x] == 255:
                inner_radii.append(r - 10)
                break

# ===============================
# 6️⃣ Calculate Averages
# ===============================
outer_mean = int(np.mean(outer_radii))
inner_mean = int(np.mean(inner_radii))

thickness = outer_mean - inner_mean

print("Outer Radius:", outer_mean)
print("Inner Radius:", inner_mean)
print("Thickness:", thickness)

# ===============================
# 7️⃣ Save Thickness Data
# ===============================
result_df = pd.DataFrame({
    "Angle": angles[:len(outer_radii)],
    "Outer_Radius": outer_radii[:len(angles)],
    "Inner_Radius": inner_radii[:len(angles)]
})

result_df.to_csv("output/thickness_data.csv", index=False)

# ===============================
# 8️⃣ Plot Thickness Graph
# ===============================
plt.figure()
plt.plot(result_df["Angle"], result_df["Outer_Radius"] - result_df["Inner_Radius"])
plt.xlabel("Angle")
plt.ylabel("Thickness")
plt.title("Ring Thickness vs Angle")
plt.savefig("output/thickness_graph.png")
plt.close()

# ===============================
# 9️⃣ Draw Circles
# ===============================
output_img = img.copy()

# Draw center (blue)
cv2.circle(output_img, (center_x, center_y), 5, (255, 0, 0), -1)

# Draw outer circle (green)
cv2.circle(output_img, (center_x, center_y), outer_mean, (0, 255, 0), 3)

# Draw inner circle (red)
cv2.circle(output_img, (center_x, center_y), inner_mean, (0, 0, 255), 3)

cv2.imwrite("output/detected_circles.jpg", output_img)

print("✅ Done! Check the output folder.")