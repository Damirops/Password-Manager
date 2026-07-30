import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "passwords.json"


def load_data():
    """Safely loads saved data from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"profile": {"gmail": "", "phone": ""}, "passwords": {}}
    return {"profile": {"gmail": "", "phone": ""}, "passwords": {}}


def save_data(data):
    """Saves data to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


class PasswordManagerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager")
        self.root.geometry("540x820")
        self.root.minsize(500, 780)

        # Modern color palette configuration
        self.bg_color = "#F8F9FA"
        self.card_bg = "#FFFFFF"
        self.success_color = "#198754"
        self.danger_color = "#DC3545"
        self.text_color = "#212529"

        self.root.configure(bg=self.bg_color)

        # Load data
        self.data = load_data()

        # Password visibility state (False = hidden, True = visible)
        self.is_password_visible = False

        # Styles for ttk components
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

        # --- MAIN CONTAINER ---
        main_container = tk.Frame(root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # App title
        title_label = tk.Label(
            main_container,
            text="Password Manager & Personal Data",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # --- UNIFIED INPUT SECTION ---
        form_frame = tk.LabelFrame(
            main_container,
            text=" Input and Edit Data ",
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

        # Special password row with eye toggle button
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

        # Save button
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

        # --- PERSONAL DATA DISPLAY SECTION (GMAIL & PHONE) ---
        info_frame = tk.LabelFrame(
            main_container,
            text=" Your Profile (View) ",
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

        # --- SAVED PASSWORDS LIST SECTION ---
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

        table_container = tk.Frame(list_frame, bg=self.card_bg, bd=1, relief="solid")
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

        # Action buttons frame below table (Edit and Delete)
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

        # Initial data load to interface
        self.load_data_to_gui()
        self.refresh_table()

    def toggle_password_visibility(self):
        """Toggles the visibility of the entered password (hides/shows characters)."""
        if self.is_password_visible:
            self.entries["password_entry"].config(show="*")
            self.eye_btn.config(bg="#E9ECEF")
            self.is_password_visible = False
        else:
            self.entries["password_entry"].config(show="")
            self.eye_btn.config(bg="#CED4DA")
            self.is_password_visible = True

    def load_data_to_gui(self):
        """Loads saved Gmail and phone number into fields and the visible preview."""
        profile = self.data.get("profile", {})
        gmail = profile.get("gmail", "")
        phone = profile.get("phone", "")

        if gmail:
            self.entries["gmail_entry"].insert(0, gmail)
        if phone:
            self.entries["phone_entry"].insert(0, phone)

        self.update_profile_display(gmail, phone)

    def update_profile_display(self, gmail, phone):
        """Updates the text display of Gmail and phone on the screen."""
        self.lbl_display_gmail.config(
            text=f"Gmail: {gmail if gmail else 'Not entered'}"
        )
        self.lbl_display_phone.config(
            text=f"Phone Number: {phone if phone else 'Not entered'}"
        )

    def save_all_data(self):
        """Collects, validates, and saves both profile and password data."""
        gmail = self.entries["gmail_entry"].get().strip()
        phone = self.entries["phone_entry"].get().strip()
        service = self.entries["service_entry"].get().strip()
        username = self.entries["username_entry"].get().strip()
        password = self.entries["password_entry"].get().strip()

        # Save personal info
        if gmail or phone:
            self.data["profile"]["gmail"] = gmail
            self.data["profile"]["phone"] = phone
            self.update_profile_display(gmail, phone)

        # Validate and save password
        if service or username or password:
            if not service or not username or not password:
                messagebox.showerror(
                    "Input Error",
                    "To save a service, you must fill out the Service Name, Username, and Password fields!",
                )
                return

            self.data["passwords"][service] = {
                "username": username,
                "password": password,
            }

            self.refresh_table()
            self.entries["service_entry"].delete(0, tk.END)
            self.entries["username_entry"].delete(0, tk.END)
            self.entries["password_entry"].delete(0, tk.END)

        # Persistent storage
        save_data(self.data)
        messagebox.showinfo("Success", "Data has been successfully saved!")

    def edit_selected_password(self):
        """Transfers the selected account's data from the table back to the edit form."""
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

        messagebox.showinfo(
            "Editing",
            (
                f"Data for '{service}' has been loaded into the form. Modify them and click"
                " 'Save Data'."
            ),
        )

    def delete_selected_password(self):
        """Deletes the selected account from the table and persistent storage."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Warning", "Please select an account from the table to delete!"
            )
            return

        item_values = self.tree.item(selected_item, "values")
        service = item_values[0]

        # Deletion confirmation
        confirm = messagebox.askyesno(
            "Delete Confirmation",
            f"Are you sure you want to delete the account for '{service}'?",
        )
        if confirm:
            # Remove from dictionary
            if service in self.data["passwords"]:
                del self.data["passwords"][service]

            # Save changes to file and refresh table
            save_data(self.data)
            self.refresh_table()
            messagebox.showinfo("Success", f"Account for '{service}' has been successfully deleted!")

    def refresh_table(self):
        """Refreshes the password table view."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        passwords = self.data.get("passwords", {})
        for service, info in passwords.items():
            self.tree.insert(
                "", tk.END, values=(service, info["username"], info["password"])
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
