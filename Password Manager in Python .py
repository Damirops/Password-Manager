import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "passwords.json"


def load_data():
  """Sigurno učitava spremljene podatke iz JSON datoteke."""
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    except json.JSONDecodeError:
      return {"profile": {"gmail": "", "phone": ""}, "passwords": {}}
  return {"profile": {"gmail": "", "phone": ""}, "passwords": {}}


def save_data(data):
  """Sprema podatke u JSON datoteku."""
  with open(DATA_FILE, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)


class PasswordManagerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Secure Password Manager")
    self.root.geometry("540x820")
    self.root.minsize(500, 780)

    # Postavljanje moderne palete boja
    self.bg_color = "#F8F9FA"
    self.card_bg = "#FFFFFF"
    self.success_color = "#198754"
    self.danger_color = "#DC3545"
    self.text_color = "#212529"

    self.root.configure(bg=self.bg_color)

    # Učitavanje podataka
    self.data = load_data()

    # Stanje vidljivosti lozinke (False = skriveno, True = vidljivo)
    self.is_password_visible = False

    # Stilovi za ttk komponente
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

    # --- GLAVNI KONTEJNER ---
    main_container = tk.Frame(root, bg=self.bg_color)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Naslov aplikacije
    title_label = tk.Label(
        main_container,
        text="Upravitelj Lozinki i Osobni Podaci",
        font=("Segoe UI", 16, "bold"),
        bg=self.bg_color,
        fg=self.text_color,
    )
    title_label.pack(anchor="w", pady=(0, 15))

    # --- JEDINSTVENA SEKCIJA ZA UNOS ---
    form_frame = tk.LabelFrame(
        main_container,
        text=" Unos i uređivanje podataka ",
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
        ("Broj telefona:", "phone_entry", 1),
        ("Naziv servisa:", "service_entry", 2),
        ("Korisničko ime:", "username_entry", 3),
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

    # Specijalni red za lozinku s gumbom za oko (Toggle)
    lbl_pass = tk.Label(
        form_frame,
        text="Lozinka:",
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

    # Gumb za spremanje
    save_btn = tk.Button(
        form_frame,
        text="Spremi podatke",
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

    # --- SEKCIJA ZA PRIKAZ OSOBNIH PODATAKA (GMAIL I TELEFON) ---
    info_frame = tk.LabelFrame(
        main_container,
        text=" Vaš profil (Prikaz) ",
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
        text="Broj telefona: -",
        font=("Segoe UI", 10),
        bg=self.card_bg,
        anchor="w",
    )
    self.lbl_display_phone.pack(anchor="w", padx=10, pady=2)

    # --- SEKCIJA ZA PRIKAZ SPREMLJENIH LOZINKI ---
    list_frame = tk.Frame(main_container, bg=self.bg_color)
    list_frame.pack(fill="both", expand=True)

    list_label = tk.Label(
        list_frame,
        text="Spremljeni računi:",
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
    self.tree.heading("Service", text="Servis")
    self.tree.heading("Username", text="Korisničko ime")
    self.tree.heading("Password", text="Lozinka")

    self.tree.column("Service", width=140, anchor="w")
    self.tree.column("Username", width=150, anchor="w")
    self.tree.column("Password", width=150, anchor="w")
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

    scrollbar = ttk.Scrollbar(
        table_container, orient="vertical", command=self.tree.yview
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree.configure(yscrollcommand=scrollbar.set)

    # Okvir za gumbe ispod tablice (Uredi i Obriši)
    btn_action_frame = tk.Frame(list_frame, bg=self.bg_color)
    btn_action_frame.pack(fill="x", pady=(5, 0))

    delete_btn = tk.Button(
        btn_action_frame,
        text="Obriši odabrani račun",
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
        text="Uredi odabrani račun",
        bg="#0D6EFD",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=self.edit_selected_password,
    )
    edit_btn.pack(side=tk.RIGHT)

    # Inicijalno učitavanje podataka u sučelje
    self.load_data_to_gui()
    self.refresh_table()

  def toggle_password_visibility(self):
    """Mjenja vidljivost upisane lozinke (skriva/prikazuje znakove)."""
    if self.is_password_visible:
      self.entries["password_entry"].config(show="*")
      self.eye_btn.config(bg="#E9ECEF")
      self.is_password_visible = False
    else:
      self.entries["password_entry"].config(show="")
      self.eye_btn.config(bg="#CED4DA")
      self.is_password_visible = True

  def load_data_to_gui(self):
    """Učitava spremljeni Gmail i broj telefona u polja i u vidljivi pregled."""
    profile = self.data.get("profile", {})
    gmail = profile.get("gmail", "")
    phone = profile.get("phone", "")

    if gmail:
      self.entries["gmail_entry"].insert(0, gmail)
    if phone:
      self.entries["phone_entry"].insert(0, phone)

    self.update_profile_display(gmail, phone)

  def update_profile_display(self, gmail, phone):
    """Ažurira tekstualni prikaz Gmail-a i telefona na ekranu."""
    self.lbl_display_gmail.config(
        text=f"Gmail: {gmail if gmail else 'Nije uneseno'}"
    )
    self.lbl_display_phone.config(
        text=f"Broj telefona: {phone if phone else 'Nije uneseno'}"
    )

  def save_all_data(self):
    """Prikuplja, validira i sprema i profil i lozinku."""
    gmail = self.entries["gmail_entry"].get().strip()
    phone = self.entries["phone_entry"].get().strip()
    service = self.entries["service_entry"].get().strip()
    username = self.entries["username_entry"].get().strip()
    password = self.entries["password_entry"].get().strip()

    # Spremanje osobnih podataka
    if gmail or phone:
      self.data["profile"]["gmail"] = gmail
      self.data["profile"]["phone"] = phone
      self.update_profile_display(gmail, phone)

    # Validacija i spremanje lozinke
    if service or username or password:
      if not service or not username or not password:
        messagebox.showerror(
            "Greška u unosu",
            "Za spremanje servisa morate popuniti Naziv, Korisničko ime i Lozinku!",
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

    # Trajno spremanje
    save_data(self.data)
    messagebox.showinfo("Uspjeh", "Podaci su uspješno spremljeni!")

  def edit_selected_password(self):
    """Prebacuje podatke odabranog računa iz tablice natrag u formu za uređivanje."""
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Upozorenje", "Molimo odaberite račun iz tablice koji želite urediti!"
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
        "Uređivanje",
        (
            f"Podaci za '{service}' su učitani u formu. Izmijenite ih i kliknite"
            " 'Spremi podatke'."
        ),
    )

  def delete_selected_password(self):
    """Briše odabrani račun iz tablice i trajne pohrane."""
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Upozorenje", "Molimo odaberite račun iz tablice koji želite obrisati!"
      )
      return

    item_values = self.tree.item(selected_item, "values")
    service = item_values[0]

    # Potvrda brisanja
    confirm = messagebox.askyesno(
        "Potvrda brisanja",
        f"Jeste li sigurni da želite obrisati račun za '{service}'?",
    )
    if confirm:
      # Ukloni iz rječnika
      if service in self.data["passwords"]:
        del self.data["passwords"][service]

      # Spremi promjene u datoteku i osvježi tablicu
      save_data(self.data)
      self.refresh_table()
      messagebox.showinfo("Uspjeh", f"Račun za '{service}' je uspješno obrisan!")

  def refresh_table(self):
    """Osvježava prikaz tablice s lozinkama."""
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
