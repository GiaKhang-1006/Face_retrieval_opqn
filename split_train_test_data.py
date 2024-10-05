import os
import shutil
import random

# Đường dẫn tuyệt đối tới dữ liệu đã resize
input_folder = '/Users/giakhangha/Documents/Face_Retrieval/opqn/dataset/facescrub/resized'
train_folder = '/Users/giakhangha/Documents/Face_Retrieval/opqn/dataset/facescrub/train'
test_folder = '/Users/giakhangha/Documents/Face_Retrieval/opqn/dataset/facescrub/test'

# Tỷ lệ chia dữ liệu (80% cho huấn luyện, 20% cho kiểm tra)
train_ratio = 0.8


def split_train_test(input_folder, train_folder, test_folder, train_ratio):
    # Duyệt qua các thư mục con (actor_faces, actress_faces)
    for root, dirs, files in os.walk(input_folder):
        for dir_name in dirs:
            subfolder_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(subfolder_path, input_folder)

            # Đường dẫn đến các thư mục train và test tương ứng
            train_subfolder = os.path.join(train_folder, relative_path)
            test_subfolder = os.path.join(test_folder, relative_path)

            # Tạo thư mục train và test nếu chưa tồn tại
            os.makedirs(train_subfolder, exist_ok=True)
            os.makedirs(test_subfolder, exist_ok=True)

            # Lấy tất cả các file ảnh trong thư mục con
            images = [f for f in os.listdir(subfolder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

            # Xáo trộn danh sách ảnh
            random.shuffle(images)

            # Tính toán số lượng ảnh cho tập huấn luyện và tập kiểm tra
            split_point = int(len(images) * train_ratio)

            # Chia ảnh vào thư mục train
            train_images = images[:split_point]
            test_images = images[split_point:]

            # Di chuyển ảnh vào thư mục train
            for image in train_images:
                src_path = os.path.join(subfolder_path, image)
                dst_path = os.path.join(train_subfolder, image)
                shutil.copy(src_path, dst_path)

            # Di chuyển ảnh vào thư mục test
            for image in test_images:
                src_path = os.path.join(subfolder_path, image)
                dst_path = os.path.join(test_subfolder, image)
                shutil.copy(src_path, dst_path)

            print(f"Processed {len(train_images)} train images and {len(test_images)} test images for {relative_path}")


if __name__ == "__main__":
    split_train_test(input_folder, train_folder, test_folder, train_ratio)
