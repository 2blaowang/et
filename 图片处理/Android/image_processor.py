import os
from PIL import Image, ImageFilter, ImageDraw

def apply_blur_and_gradient(input_image_path, output_folder, blur_radius):
    try:
        # 获取输入图片的文件名和扩展名
        base_name = os.path.basename(input_image_path)
        name, ext = os.path.splitext(base_name)

        # 生成输出文件名
        output_image_name = f"{name}_processed{ext}"
        output_image_path = os.path.join(output_folder, output_image_name)

        # 打开图片
        image = Image.open(input_image_path)
        
        # 应用高斯模糊
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # 创建一个与原图大小相同的渐变遮罩
        gradient_mask = Image.new('L', (blurred_image.width, blurred_image.height), 0)
        draw = ImageDraw.Draw(gradient_mask)
        
        # 从上至下创建渐变效果
        for y in range(blurred_image.height):
            alpha = int(255 * (y / blurred_image.height))
            draw.line([(0, y), (blurred_image.width, y)], fill=alpha)
        
        # 将渐变遮罩应用到模糊图片上
        result_image = Image.new('RGB', (blurred_image.width, blurred_image.height), (255, 255, 255))
        result_image.paste(blurred_image, (0, 0), mask=gradient_mask)
        
        # 保存结果图片
        result_image.save(output_image_path)

        return True, "处理完成"
    except Exception as e:
        return False, f"处理失败: {str(e)}"