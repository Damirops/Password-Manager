import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error

#Potrebna  bilbloteka za rad za mysql su dve stvari:

# 1. pip install mysql-connector-python     => cmd (command promt)
# 2.  moram biti instaliran Xampp sa najvovijom apach2 i mysql
#   (ne nužno može koja je srednja verzija xamppa)   


# Default XAMPP MySQL konfiguracija
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "password_manager"
JSON_BACKUP_FILE = "passwords.json"


def check_mysql_connection():
    """Provjerava je li XAMPP MySQL server aktivan i vraća popis svih baza."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]

            # Ispis svih baza u konzolu
            print("--- Detektirane MySQL baze na serveru ---")
            for db in databases:
                print(f"- {db}")
            print("---------------------------------------")

            # Stvori bazu 'password_manager' ako još ne postoji
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            conn.commit()
            cursor.close()
            conn.close()
            return True, databases
    except Error as e:
        print(f"MySQL greška pri spajanju: {e}")
        return False, []
    return False, []


def get_db_connection():
    """Ostvaruje vezu s 'password_manager' bazom."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        return conn
    except Error:
        return None


def init_db_tables():
    """Inicijalizira tablice u MySQL bazi ako ne postoje."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                id INT PRIMARY KEY DEFAULT 1,
                gmail VARCHAR(255),
                phone VARCHAR(255)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                service VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()


class PasswordManagerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager (MySQL Integration)")
        self.root.geometry("560x880")
        self.root.minsize(500, 800)

        self.bg_color = "#F8F9FA"
        self.card_bg = "#FFFFFF"
        self.success_color = "#198754"
        self.danger_color = "#DC3545"
        self.text_color = "#212529"

        self.root.configure(bg=self.bg_color)
        self.is_password_visible = False

        # --- PROVJERA MYSQL STATUSA ---
        self.mysql_active, self.mysql_databases = check_mysql_connection()
        if self.mysql_active:
            init_db_tables()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview",
            background="white",
            foreground=self.text_color,
            rowheight=25,
            fieldbackground="white",
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#E9ECEF",
            foreground=self.text_color,
        )

        main_container = tk.Frame(root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=15)

        # Naslov i indikator MySQL statusa
        title_label = tk.Label(
            main_container,
            text="Password Manager & Personal Data",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        title_label.pack(anchor="w", pady=(0, 5))

        status_text = (
            " MySQL Status: Aktivan (XAMPP)"
            if self.mysql_active
            else " MySQL Status: Neaktivan (Korisit se JSON backup)"
        )
        status_color = "#198754" if self.mysql_active else "#DC3545"

        status_label = tk.Label(
            main_container,
            text=status_text,
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_color,
            fg=status_color,
        )
        status_label.pack(anchor="w", pady=(0, 10))

        # Prikaz svih baza na serveru
        db_list_str = (
            ", ".join(self.mysql_databases)
            if self.mysql_databases
            else "Nema dostupnih baza"
        )
        db_label = tk.Label(
            main_container,
            text=f"Detektirane baze na serveru: {db_list_str}",
            font=("Segoe UI", 8, "italic"),
            bg=self.bg_color,
            fg="#6C757D",
            wraplength=500,
            justify="left",
        )
        db_label.pack(anchor="w", pady=(0, 10))

        # --- UNOS PODATAKA ---
        form_frame = tk.LabelFrame(
            main_container,
            text=" Data Entry & Edit ",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            bd=1,
            relief="solid",
        )
        form_frame.pack(fill="x", pady=(0, 15), ipadx=10, ipady=10)
        form_frame.grid_columnconfigure(1, weight=1)

        fields = [
            ("Gmail:", "gmail_entry", 0),
            ("Phone Number:", "phone_entry", 1),
            ("Service Name:", "service_entry", 2),
            ("Username:", "username_entry", 3),
        ]

        self.entries = {}
        for label_text, attr_name, row in fields:
            lbl = tk.Label(
                form_frame,
                text=label_text,
                font=("Segoe UI", 10),
                bg=self.card_bg,
                anchor="w",
            )
            lbl.grid(row=row, column=0, sticky="w", padx=10, pady=5)

            entry = tk.Entry(
                form_frame, font=("Segoe UI", 10), relief="solid", bd=1
            )
            entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            self.entries[attr_name] = entry

        lbl_pass = tk.Label(
            form_frame,
            text="Password:",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            anchor="w",
        )
        lbl_pass.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        pass_container = tk.Frame(form_frame, bg=self.card_bg)
        pass_container.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        pass_container.grid_columnconfigure(0, weight=1)

        self.entries["password_entry"] = tk.Entry(
            pass_container, font=("Segoe UI", 10), show="*", relief="solid", bd=1
        )
        self.entries["password_entry"].grid(
            row=0, column=0, sticky="ew", ipady=1
        )

        self.eye_btn = tk.Button(
            pass_container,
            text=" 👁 ",
            font=("Segoe UI", 9),
            bg="#E9ECEF",
            relief="flat",
            cursor="hand2",
            command=self.toggle_password_visibility,
        )
        self.eye_btn.grid(row=0, column=1, padx=(5, 0))

        save_btn = tk.Button(
            form_frame,
            text="Save Data",
            bg=self.success_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            activebackground="#157347",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.save_all_data,
        )
        save_btn.grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(12, 5)
        )

        # --- PRIKAZ PROFILA ---
        info_frame = tk.LabelFrame(
            main_container,
            text=" Your Profile (Overview) ",
            font=("Segoe UI", 10, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            bd=1,
            relief="solid",
        )
        info_frame.pack(fill="x", pady=(0, 15), padx=2, ipadx=5, ipady=5)

        self.lbl_display_gmail = tk.Label(
            info_frame,
            text="Gmail: -",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            anchor="w",
        )
        self.lbl_display_gmail.pack(anchor="w", padx=10, pady=2)

        self.lbl_display_phone = tk.Label(
            info_frame,
            text="Phone Number: -",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            anchor="w",
        )
        self.lbl_display_phone.pack(anchor="w", padx=10, pady=2)

        # --- TABLICA RAČUNA ---
        list_frame = tk.Frame(main_container, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True)

        list_label = tk.Label(
            list_frame,
            text="Saved Accounts:",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        list_label.pack(anchor="w", pady=(0, 5))

        table_container = tk.Frame(
            list_frame, bg=self.card_bg, bd=1, relief="solid"
        )
        table_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_container,
            columns=("Service", "Username", "Password"),
            show="headings",
            height=5,
        )
        self.tree.heading("Service", text="Service")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")

        self.tree.column("Service", width=140, anchor="w")
        self.tree.column("Username", width=150, anchor="w")
        self.tree.column("Password", width=150, anchor="w")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(
            table_container, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        btn_action_frame = tk.Frame(list_frame, bg=self.bg_color)
        btn_action_frame.pack(fill="x", pady=(5, 0))

        delete_btn = tk.Button(
            btn_action_frame,
            text="Delete Selected Account",
            bg=self.danger_color,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.delete_selected_password,
        )
        delete_btn.pack(side=tk.LEFT)

        edit_btn = tk.Button(
            btn_action_frame,
            text="Edit Selected Account",
            bg="#0D6EFD",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.edit_selected_password,
        )
        edit_btn.pack(side=tk.RIGHT)

        self.load_profile_data()
        self.refresh_table()

    def toggle_password_visibility(self):
        if self.is_password_visible:
            self.entries["password_entry"].config(show="*")
            self.eye_btn.config(bg="#E9ECEF")
            self.is_password_visible = False
        else:
            self.entries["password_entry"].config(show="")
            self.eye_btn.config(bg="#CED4DA")
            self.is_password_visible = True

    def load_profile_data(self):
        gmail, phone = "", ""
        if self.mysql_active:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT gmail, phone FROM profile WHERE id = 1"
                )
                row = cursor.fetchone()
                if row:
                    gmail, phone = row[0], row[1]
                cursor.close()
                conn.close()
        elif os.path.exists(JSON_BACKUP_FILE):
            try:
                with open(JSON_BACKUP_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    gmail = data.get("profile", {}).get("gmail", "")
                    phone = data.get("profile", {}).get("phone", "")
            except json.JSONDecodeError:
                pass

        if gmail:
            self.entries["gmail_entry"].insert(0, gmail)
        if phone:
            self.entries["phone_entry"].insert(0, phone)
        self.update_profile_display(gmail, phone)

    def update_profile_display(self, gmail, phone):
        self.lbl_display_gmail.config(
            text=f"Gmail: {gmail if gmail else 'Not set'}"
        )
        self.lbl_display_phone.config(
            text=f"Phone Number: {phone if phone else 'Not set'}"
        )

    def save_all_data(self):
        gmail = self.entries["gmail_entry"].get().strip()
        phone = self.entries["phone_entry"].get().strip()
        service = self.entries["service_entry"].get().strip()
        username = self.entries["username_entry"].get().strip()
        password = self.entries["password_entry"].get().strip()

        if self.mysql_active:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                if gmail or phone:
                    cursor.execute(
                        """
                        INSERT INTO profile (id, gmail, phone) 
                        VALUES (1, %s, %s)
                        ON DUPLICATE KEY UPDATE gmail=%s, phone=%s
                    """,
                        (gmail, phone, gmail, phone),
                    )
                    self.update_profile_display(gmail, phone)

                if service or username or password:
                    if not service or not username or not password:
                        messagebox.showerror(
                            "Input Error",
                            "To save a service, fill out Service Name, Username, and Password!",
                        )
                        return
                    cursor.execute(
                        """
                        INSERT INTO accounts (service, username, password) 
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE username=%s, password=%s
                    """,
                        (service, username, password, username, password),
                    )

                conn.commit()
                cursor.close()
                conn.close()
                self.refresh_table()
                self.clear_service_entries()
                messagebox.showinfo(
                    "Success", "Data saved successfully to MySQL database!"
                )
        else:
            # Fallback na JSON datoteku ako MySQL nije uključen
            data = {"profile": {"gmail": "", "phone": ""}, "passwords": {}}
            if os.path.exists(JSON_BACKUP_FILE):
                try:
                    with open(JSON_BACKUP_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    pass

            if gmail or phone:
                data["profile"] = {"gmail": gmail, "phone": phone}
                self.update_profile_display(gmail, phone)

            if service or username or password:
                if not service or not username or not password:
                    messagebox.showerror(
                        "Input Error",
                        "To save a service, fill out Service Name, Username, and Password!",
                    )
                    return
                data["passwords"][service] = {
                    "username": username,
                    "password": password,
                }

            with open(JSON_BACKUP_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.refresh_table()
            self.clear_service_entries()
            messagebox.showinfo(
                "Saved locally",
                "MySQL inactive. Data saved to JSON fallback file.",
            )

    def clear_service_entries(self):
        self.entries["service_entry"].delete(0, tk.END)
        self.entries["username_entry"].delete(0, tk.END)
        self.entries["password_entry"].delete(0, tk.END)

    def edit_selected_password(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Warning", "Please select an account from the table to edit!"
            )
            return

        item_values = self.tree.item(selected_item, "values")
        service, username, password = item_values

        self.entries["service_entry"].delete(0, tk.END)
        self.entries["service_entry"].insert(0, service)

        self.entries["username_entry"].delete(0, tk.END)
        self.entries["username_entry"].insert(0, username)

        self.entries["password_entry"].delete(0, tk.END)
        self.entries["password_entry"].insert(0, password)

    def delete_selected_password(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Warning", "Please select an account from the table to delete!"
            )
            return

        service = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno(
            "Confirm Deletion", f"Are you sure you want to delete '{service}'?"
        )
        if not confirm:
            return

        if self.mysql_active:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM accounts WHERE service = %s", (service,)
                )
                conn.commit()
                cursor.close()
                conn.close()
        else:
            if os.path.exists(JSON_BACKUP_FILE):
                with open(JSON_BACKUP_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if service in data.get("passwords", {}):
                    del data["passwords"][service]
                with open(JSON_BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        self.refresh_table()
        messagebox.showinfo("Success", f"Account '{service}' deleted!")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.mysql_active:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT service, username, password FROM accounts"
                )
                for row in cursor.fetchall():
                    self.tree.insert("", tk.END, values=(row[0], row[1], row[2]))
                cursor.close()
                conn.close()
        elif os.path.exists(JSON_BACKUP_FILE):
            try:
                with open(JSON_BACKUP_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for service, info in data.get("passwords", {}).items():
                        self.tree.insert(
                            "",
                            tk.END,
                            values=(
                                service,
                                info["username"],
                                info["password"],
                            ),
                        )
            except json.JSONDecodeError:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
