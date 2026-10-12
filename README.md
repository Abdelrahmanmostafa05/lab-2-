
# DB Lab 2: Login & To-Do Application

## 1. Team Members
Name: Abdelrahman Mostafa Shawky 
ID: 2304035
group: 2
section: 2

Name: Ziad Mohamed Fathy 
ID: 2304031
group: 2
section: 2

---

 2. Technologies Used
Back-end: Python (Flask), PyMySQL, bcrypt, python-dotenv
Front-end: HTML5, CSS3, JavaScript (Vanilla JS), Bootstrap 5
Database: MySQL

---

3. Features Built (R1 - R10)

R1 (Register): Full registration flow with duplicate email detection (`Email Already Exists`) and auto-login upon success.
R2 (Login & Logout): Secure authentication returning unified error message `Invalid email or password`. Logout clears session.
R3 (Private List): Protected route using session checks; non-authenticated users are redirected to login. Tasks displayed newest first.
R4 (Add To-Do): Adding tasks with title length and presence validation.
R5 (Edit Title): Inline updating of existing tasks.
R6 (Toggle Status): Mark tasks as done/not done.
R7 (Delete To-Do): Task deletion with client-side JavaScript confirmation prompt.
R8 (Dual Validation): Client-side JS validation and server-side Python validation enforcing identical rule messages without redundant DB hits on error.
R9 (Security): Passwords hashed via `bcrypt`. All SQL queries parameterized with placeholders (`%s`). User identification strictly bound to session `user_id`.
R10 (UI/UX): Responsive Bootstrap 5 interface, clean empty states, mobile-friendly design, and custom 404/500 error pages.

---

4. Lab Questions & Answers

(a) Why do `UPDATE` and `DELETE` contain `AND user_id = ?` and what changes if you remove it?

Answer: It enforces authorization at the database query level (Horizontal Access Control). Since task IDs come from browser requests, a malicious user could tamper with the `todo_id` to edit or delete someone else's tasks. Adding `AND user_id = ?` ensures queries only affect rows belonging to the currently logged-in user. If removed, any logged-in user could alter or delete any task in the entire database.

(b) What happens if you insert a to-do for a `user_id` that does not exist, and which constraint of the lecture is that?

Answer: MySQL rejects the query and throws Error 1452 (Cannot add or update a child row: a foreign key constraint fails). This is the **Foreign Key Constraint** (Referential Integrity).

(c) Why do you store a hash and not the password?

Answer: To protect user security in the event of a database breach. Hashes created with algorithms like `bcrypt` are salted and computationally slow, making them irreversible and resistant to dictionary or rainbow table attacks.

 (d) The `name` column is `NOT NULL`: why did you still need your own check for an empty name?

Answer: In SQL, `NOT NULL` prevents `NULL` entries, but accepts empty strings (`""`) or whitespace strings (`"   "`). Custom validation in code ensures that names are non-empty and visually valid text.
