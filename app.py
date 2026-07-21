import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

st.set_page_config(page_title="图片拼接工具", page_icon="🖼️", layout="wide")

FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "MSYHBD.TTC")

@st.cache_resource
def load_font(size):
    try:
        if os.path.exists(FONT_PATH):
            return ImageFont.truetype(FONT_PATH, size, index=0)
    except: pass
    try:
        return ImageFont.truetype(FONT_PATH, size, index=1)
    except: pass
    return ImageFont.load_default()

st.title("🖼️ 图片拼接工具")
st.markdown("上传两张图片，将它们拼接在一起，并添加自定义文字。")

with st.sidebar:
    st.header("⚙️ 拼接设置")
    stitch_mode = st.radio("拼接方向", options=["垂直拼接（上下）", "水平拼接（左右）"], index=0)
    vertical = stitch_mode.startswith("垂直")
    align_mode = st.radio("对齐方式", options=["居中对齐", "左/上对齐", "右/下对齐"], index=0)
    bg_color = st.color_picker("背景颜色", "#FFFFFF")
    st.divider()
    st.header("📝 文字设置")
    text_input = st.text_area("输入文字（支持多行）", value="", height=100)
    text_position = st.selectbox("文字位置", options=["顶部", "底部", "左上角", "右上角", "左下角", "右下角", "居中"], index=0)
    font_size = st.slider("字体大小", min_value=10, max_value=200, value=40, step=1)
    text_color = st.color_picker("文字颜色", "#000000")
    text_offset_x = st.slider("水平偏移", min_value=-500, max_value=500, value=0, step=1)
    text_offset_y = st.slider("垂直偏移", min_value=-500, max_value=500, value=0, step=1)
    st.divider()
    st.header("💾 输出设置")
    output_format = st.selectbox("输出格式", options=["PNG", "JPEG"], index=0)
    if output_format == "JPEG": jpeg_quality = st.slider("JPEG 质量", min_value=10, max_value=100, value=95, step=5)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📷 图片 1")
    img1_file = st.file_uploader("上传第一张图片", type=["png", "jpg", "jpeg", "webp", "bmp"], key="img1")
    img1 = Image.open(img1_file).convert("RGBA") if img1_file else None
    if img1: st.image(img1, caption=f"图片 1 — {img1.size[0]}×{img1.size[1]}", use_container_width=True)
with col2:
    st.subheader("📷 图片 2")
    img2_file = st.file_uploader("上传第二张图片", type=["png", "jpg", "jpeg", "webp", "bmp"], key="img2")
    img2 = Image.open(img2_file).convert("RGBA") if img2_file else None
    if img2: st.image(img2, caption=f"图片 2 — {img2.size[0]}×{img2.size[1]}", use_container_width=True)

def stitch_images(img_a, img_b, vertical, align, bg):
    if vertical: new_w, new_h = max(img_a.width, img_b.width), img_a.height + img_b.height
    else: new_w, new_h = img_a.width + img_b.width, max(img_a.height, img_b.height)
    canvas = Image.new("RGBA", (new_w, new_h), bg)
    if vertical:
        if align == "居中对齐": x_a, x_b = (new_w - img_a.width) // 2, (new_w - img_b.width) // 2
        elif align == "左/上对齐": x_a, x_b = 0, 0
        else: x_a, x_b = new_w - img_a.width, new_w - img_b.width
        canvas.paste(img_a, (x_a, 0), img_a)
        canvas.paste(img_b, (x_b, img_a.height), img_b)
    else:
        if align == "居中对齐": y_a, y_b = (new_h - img_a.height) // 2, (new_h - img_b.height) // 2
        elif align == "左/上对齐": y_a, y_b = 0, 0
        else: y_a, y_b = new_h - img_a.height, new_h - img_b.height
        canvas.paste(img_a, (0, y_a), img_a)
        canvas.paste(img_b, (img_a.width, y_b), img_b)
    return canvas

def add_text_to_image(img, text, position, font_size, color, offset_x, offset_y):
    if not text.strip(): return img
    draw = ImageDraw.Draw(img)
    font = load_font(font_size)
    lines = text.split("\n")
    lh, lw = [], []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw.append(bbox[2] - bbox[0])
        lh.append(bbox[3] - bbox[1])
    th = sum(lh) + (len(lines) - 1) * 4
    mw = max(lw) if lw else 0
    w, h = img.size
    p = 20
    pm = {"顶部": (w // 2, p), "底部": (w // 2, h - th - p), "左上角": (p, p), "右上角": (w - mw - p, p), "左下角": (p, h - th - p), "右下角": (w - mw - p, h - th - p), "居中": (w // 2, h // 2 - th // 2)}
    bx, by = pm.get(position, (w // 2, p))
    bx += offset_x; by += offset_y
    cy = by
    for i, line in enumerate(lines):
        if position in ("顶部", "底部", "居中"): x = bx - lw[i] // 2
        elif position in ("左上角", "左下角"): x = bx
        else: x = bx + mw - lw[i]
        draw.text((x, cy), line, fill=color, font=font)
        cy += lh[i] + 4
    return img

if img1 and img2:
    st.divider()
    st.subheader("🔧 拼接结果")
    result = stitch_images(img1, img2, vertical, align_mode, bg_color)
    if text_input.strip(): result = add_text_to_image(result, text_input, text_position, font_size, text_color, text_offset_x, text_offset_y)
    st.image(result, caption=f"拼接结果 — {result.size[0]}×{result.size[1]}", use_container_width=True)
    buf = io.BytesIO()
    if output_format == "PNG":
        result.save(buf, format="PNG")
        mime, ext = "image/png", "png"
    else:
        result = result.convert("RGB")
        result.save(buf, format="JPEG", quality=jpeg_quality)
        mime, ext = "image/jpeg", "jpg"
    buf.seek(0)
    st.download_button(label=f"📥 下载拼接图片（.{ext}）", data=buf, file_name=f"stitched_image.{ext}", mime=mime, use_container_width=True)
else:
    st.info("👆 请上传两张图片以开始拼接。")

