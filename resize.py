import os
from PIL import Image

# Đường dẫn đến thư mục chứa ảnh gốc và thư mục lưu ảnh đã resize
input_folder = '/Users/giakhangha/Documents/Face_Retrieval/opqn/dataset/facescrub/original'
output_folder = '/Users/giakhangha/Documents/Face_Retrieval/opqn/dataset/facescrub/resized'

# Kích thước mong muốn cho các ảnh (phù hợp cho ResNet)
target_size = (224, 224)


def resize_images(input_folder, output_folder, target_size):
    # Kiểm tra nếu thư mục đầu vào không tồn tại
    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist.")
        return

    # Duyệt qua các thư mục con trong thư mục input
    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Đường dẫn đầy đủ tới ảnh
                file_path = os.path.join(root, file_name)

                # Tạo đường dẫn tương ứng trong thư mục output
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)

                # Tạo thư mục đầu ra nếu chưa tồn tại
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)

                try:
                    # Mở và resize ảnh
                    img = Image.open(file_path)
                    img_resized = img.resize(target_size)

                    # Đường dẫn lưu ảnh đã resize
                    output_image_path = os.path.join(output_subfolder, file_name)
                    img_resized.save(output_image_path)
                    print(f"Successfully resized and saved: {output_image_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    resize_images(input_folder, output_folder, target_size)
