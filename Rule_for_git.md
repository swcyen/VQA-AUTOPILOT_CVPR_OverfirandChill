# Cấu trúc Branch

Các branch chính:

* `main` – Code ổn định dùng cho production
* `dev` – Branch tích hợp code từ các developer
* `feature/<name>` – Branch riêng của từng người


```
main
 └── dev
      ├── feature/sang
      ├── feature/nhi
      └── feature/huy
```

Mỗi lập trình viên **chỉ làm việc trên branch của mình**.

---

# Thiết lập

Clone repository:

```
git clone <repo-url>
cd <repo-name>
```

Chuyển sang branch dev và tạo branch riêng:

```
git checkout dev
git checkout -b feature/<ten-cua-ban>
```

Ví dụ:

```
git checkout -b feature/huy
```

Push branch lên remote:

```
git push -u origin feature/<ten-cua-ban>
```

---

## 1. Cập nhật code mới nhất

```
git checkout dev
git pull origin dev
```

Cập nhật branch của mình:

```
git checkout feature/<ten-cua-ban>
git merge dev
```

Branch có code mới nhất từ team.

---

## 2. Code và Commit

Sau khi thay đổi code:

```
git add .
git commit -m "mô tả thay đổi"
```

Push code lên:

```
git push
```

---

# Merge vào dev

Khi hoàn thành feature:

1. Push branch
2. Tạo **Pull Request (PR)**

```
feature/<ten-cua-ban> → dev
```

Em se review trước khi merge.

---

# Merge dev vào main

Khi hệ thống đã ổn định:

```
dev → main
```

Chỉ những code **đã test và ổn định** mới được merge vào `main`.

---

# Xử lý Conflict

Nếu Git báo conflict:

```
git pull origin dev
```

Sửa file bị conflict, sau đó:

```
git add .
git commit
git push
```

---

# Quy tắc cơ bản

1. **Không push trực tiếp vào `main`.**
2. Luôn làm việc trên branch của mình.
3. Viết commit message rõ ràng.

---

# Tóm tắt lệnh thường dùng

Tạo branch:

```
git checkout -b feature/<name>
```

Commit thay đổi:

```
git add .
git commit -m "message"
```

Push branch:

```
git push -u origin feature/<name>
```

Cập nhật branch:

```
git checkout dev
git pull origin dev
git checkout feature/<name>
git merge dev
```

---
Quan trong:
* Không dùng `git push --force` 

# Công cụ hỗ trợ

Một số công cụ GUI giúp dùng Git dễ hơn:

* GitHub Desktop
* GitKraken
* VSCode Git integration

---

