# bot_find_socials
Find Linkedin, Twitter and Facebook accounts.<br>
Chạy bằng file .exe:<br>
<strong>Hướng dẫn sử dụng :</strong><br>
<strong>Tool là file <i>find_socials.exe</i> trong thư mục <code>dist</code>, hoặc có thể tải trực tiếp bằng link sau: <a href="https://drive.google.com/file/d/19o0lpbDUqbazQc6dlDOHam0cA-albBpT/view?usp=sharing">Windows</a>, <a href ="https://drive.google.com/file/d/1CmvE51ngNiqcubbs-Hb1v0qCS2_7xFYo/view?usp=sharing">Linux </a></strong>, giải nén ra và chạy file exe không cần clone repo này về.
<br>
<br>
- B1: Sử dụng file <b>input.xlsx</b> và chuẩn bị dữ liệu theo như file : cột Company Name add tên công ty cần tìm vào , cột Key Valuant add từ khóa tương ứng (Ở đây sử dụng "CEO") cần tìm vào : ví dụ: CEO, Founder. 

![image](https://github.com/TAHKInteractingAI/bot_find_socials/assets/79317931/f7ba4585-eb3c-4883-b097-68d5be580c57)

<br>
- B2: Run file <b>find_socials.exe</b>

![image](https://github.com/TAHKInteractingAI/bot_find_socials/assets/79317931/43478069-de03-4bdb-bf34-b37dc6155d15)

<br>
- B3: Chọn Browser để upload file excel đã chuẩn bị ở bước 1 lên tool, sau đó nhấn chọn Linkedin, Twitter, Facebook theo nhu cầu, chờ tool chạy tự động<br>
Chạy bằng file .py (Có sẵn python>=3.10):<br>
<code>pip install -r requirements.txt</code><br>
<code>python find_socials.py</code>

Cách run tool trên server: mở terminal, chạy lên dưới
---> cd Downloads
---> source activate test
---> python find_socials.py
