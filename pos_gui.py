import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import yaml
from src.open_parser_yaml import OpenApiParser
from src.client import ApiClient
from src.validator_response import check_api_response


class POSConnectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=("Consolas", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', '#E5F3FF')])
        
        # Включаем линии сетки
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        self.root.title("POSConnector Tester GUI (Python)")
        self.root.geometry("1000x800")

        self.client = ApiClient()
        self.parser = OpenApiParser('config/operation.yaml')
        self.request_data = {}      # храним текущий запрос (для возможного редактирования)
        self.response_data = {}

        self.create_widgets()

    def create_widgets(self):
        # ===================== ЛЕВАЯ ПАНЕЛЬ =====================
        left_frame = ttk.LabelFrame(self.root, text="Транзакция", padding=12)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Список операций
        ttk.Label(left_frame, text="Операция:").pack(anchor=tk.W, pady=(0, 4))
        
        try:
            available_operations = self.parser.get_available_operations()
        except AttributeError:
            available_operations = ["sale", "refund", "customerreversal", "closebatch", "activate", 
                                   "preauthorization", "completion", "test", "print"]

        self.operation_var = tk.StringVar(value="sale")
        self.op_combo = ttk.Combobox(
            left_frame, textvariable=self.operation_var,
            values=sorted(set(op.lower() for op in available_operations)),
            state="readonly", width=30
        )
        self.op_combo.pack(fill=tk.X, pady=2)
        self.op_combo.bind("<<ComboboxSelected>>", lambda e: self.build_request_preview())

        """ttk.Label(left_frame, text="Тип активации (только для activate):").pack(anchor=tk.W, pady=(12, 4))
        self.activate_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.activate_var).pack(fill=tk.X, pady=2)
        """

        ttk.Button(left_frame, text="Отправить", command=self.execute_operation)\
            .pack(fill=tk.X, pady=(20, 6))
        
        """ttk.Button(left_frame, text="Массовое редактирование", command=self.mass_edit)\
            .pack(fill=tk.X)
        """

        # ===================== ПРАВАЯ ЧАСТЬ =====================
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Запрос ---
        req_frame = ttk.LabelFrame(main_frame, text="Запрос")
        req_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        self.request_tree = ttk.Treeview(req_frame, columns=("Value",), show="tree headings")
        self.request_tree.heading("#0", text="Поле / Ключ")
        self.request_tree.heading("Value", text="Значение")
        self.request_tree.column("#0", width=380, minwidth=300)
        self.request_tree.column("Value", width=450)

        # Включаем видимые границы (линии между строками и столбцами)
        self.request_tree.configure(show="tree headings", style="Treeview")
        self.request_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.request_tree.bind("<Double-1>", self.on_double_click_request)

        # --- Ответ ---
        resp_frame = ttk.LabelFrame(main_frame, text="Ответ")
        resp_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        self.response_tree = ttk.Treeview(resp_frame, columns=("Value",), show="tree headings")
        self.response_tree.heading("#0", text="Поле / Ключ")
        self.response_tree.heading("Value", text="Значение")
        self.response_tree.column("#0", width=380, minwidth=300)
        self.response_tree.column("Value", width=450)

        self.response_tree.configure(show="tree headings")
        self.response_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ===================== СТАТУС =====================
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)

        self.state_var = tk.StringVar(value="Current state: IDLE")
        ttk.Label(status_frame, textvariable=self.state_var, relief=tk.SUNKEN, anchor="w")\
            .pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.error_var = tk.StringVar(value="Last exchange error: ")
        ttk.Label(status_frame, textvariable=self.error_var, relief=tk.SUNKEN, anchor="w")\
            .pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def _setup_tree(self, tree):
        tree.heading("Name", text="Name")
        tree.heading("Value", text="Value")
        tree.heading("Flag", text="Flag")
        
        tree.column("Name", width=320, minwidth=200)
        tree.column("Value", width=380, minwidth=250)
        tree.column("Flag", width=50, anchor=tk.CENTER)

    def reload_config(self):
        try:
            self.parser = OpenApiParser('config/operation.yaml')
            self.state_var.set("Current state: IDLE (конфиг перезагружен)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось перечитать конфиг:\n{e}")

    def execute_operation(self):
        operation = self.operation_var.get().strip()
        activate = self.activate_var.get().strip() if operation == "activate" else None

        if operation.lower() == "close":
            self.root.quit()
            return

        self.state_var.set("Current state: EXECUTING...")
        self.error_var.set("Last exchange error: ")

        try:
            # Строим запрос
            operation_request = self.parser.build_request_example(operation, activate)
            self.request_data = operation_request

            # Показываем запрос в дереве
            self._populate_tree(self.request_tree, operation_request)

            print(f"DEBUG: Отправка операции '{operation}'")

            # Отправляем запрос
            response = self.client.send_request(operation_request)
            self.parser.old_response = response
            self.response_data = response

            # Показываем ответ в дереве
            self._populate_tree(self.response_tree, response)

            # Обработка receiptData (если есть)
            try:
                if 'response' in response and 'receiptData' in response['response']:
                    self.client.format_receipt(response['response']['receiptData'])
            except Exception as e:
                print(f"Ошибка форматирования чека: {e}")

            # Валидация ответа
            required_fields = self.parser.get_response_required_fields(operation)
            check_api_response(response.get('response', {}), required_fields)

            self.state_var.set("Current state: IDLE")

        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "sale" in error_msg.lower():
                error_msg = f"Операция '{operation}' не найдена в конфиге.\nУбедитесь, что название написано маленькими буквами."
            
            self.error_var.set(f"Last exchange error: {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
            self.state_var.set("Current state: IDLE")

        except Exception as e:
            import traceback
            full_error = traceback.format_exc()
            print("=== ПОЛНЫЙ TRACEBACK ===\n", full_error)
            
            self.error_var.set(f"Last exchange error: {str(e)}")
            messagebox.showerror("Ошибка выполнения", str(e))
            self.state_var.set("Current state: IDLE")

    def _populate_tree(self, tree, data, parent=""):
        """Иерархическое отображение JSON без {...} — всё сразу раскрыто"""
        # Полностью очищаем дерево
        for item in tree.get_children():
            tree.delete(item)

        def insert_items(d, parent_id=""):
            if isinstance(d, dict):
                for key, value in d.items():
                    display_key = f'"{key}"' if isinstance(key, str) else str(key)

                    if isinstance(value, (dict, list)):
                        # Создаём узел и сразу рекурсивно заполняем его детей
                        node = tree.insert(parent_id, "end", text=display_key, values=("",))
                        insert_items(value, node)
                    else:
                        # Простое значение
                        value_str = f'"{value}"' if isinstance(value, str) else str(value)
                        tree.insert(parent_id, "end", text=display_key, values=(value_str,))

            elif isinstance(d, list):
                for i, item in enumerate(d):
                    key = f"[{i}]"
                    if isinstance(item, (dict, list)):
                        node = tree.insert(parent_id, "end", text=key, values=("",))
                        insert_items(item, node)
                    else:
                        value_str = f'"{item}"' if isinstance(item, str) else str(item)
                        tree.insert(parent_id, "end", text=key, values=(value_str,))

            else:
                # Если пришло одиночное значение
                tree.insert(parent_id, "end", text=str(d), values=("",))

        insert_items(data)

        # ←←← Важно: раскрываем ВСЁ дерево по умолчанию
        self._expand_all(tree)

    def _expand_all(self, tree, parent=""):
        """Рекурсивно раскрывает все узлы дерева"""
        for child in tree.get_children(parent):
            tree.item(child, open=True)
            self._expand_all(tree, child)

    def _flatten_dict(self, d, prefix=""):
        """Превращаем словарь в строки таблицы (рекурсивно)"""
        rows = []
        for k, v in d.items():
            key_display = f"{prefix}.{k}" if prefix else k

            if isinstance(v, dict):
                rows.append((key_display, k, "{...}", "O"))
                rows.extend(self._flatten_dict(v, key_display))
            elif isinstance(v, list):
                val_str = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
                rows.append((key_display, k, val_str, "O"))
            else:
                flag = "M" if any(x in str(k).lower() for x in ["amount", "code", "id", "status"]) else "O"
                rows.append((key_display, k, str(v), flag))
        return rows

    def on_double_click_request(self, event):
        """Редактирование значения в таблице Запрос по двойному клику"""
        item = self.request_tree.identify('item', event.x, event.y)
        column = self.request_tree.identify('column', event.x, event.y)

        if not item or column != '#3':   # #3 = колонка Value
            return

        # Получаем текущее значение
        current_value = self.request_tree.item(item, "values")[2]

        # Создаём всплывающее окно для редактирования
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Редактировать значение")
        edit_win.geometry("400x120")
        edit_win.resizable(False, False)
        edit_win.transient(self.root)
        edit_win.grab_set()

        ttk.Label(edit_win, text="Новое значение:").pack(pady=5)
        entry = ttk.Entry(edit_win, width=50)
        entry.insert(0, current_value)
        entry.pack(pady=5, padx=10)
        entry.focus()

        def save_edit():
            new_value = entry.get().strip()
            values = list(self.request_tree.item(item, "values"))
            values[2] = new_value
            self.request_tree.item(item, values=values)
            edit_win.destroy()

        ttk.Button(edit_win, text="Сохранить", command=save_edit).pack(pady=10)

    def build_request_preview(self):
        """Автоматически показывает запрос при выборе операции в комбобоксе"""
        operation = self.operation_var.get().strip()
        if not operation:
            return

        self.state_var.set(f"Current state: Building preview for '{operation}'...")

        try:
            activate = self.activate_var.get().strip() if operation == "activate" else None
            
            operation_request = self.parser.build_request_example(operation, activate)
            self.request_data = operation_request
            
            # ←←← Вот сюда вставляем новый метод
            self._populate_tree(self.request_tree, operation_request)
            
            self.state_var.set(f"Current state: Request preview for '{operation}' ready")
            
        except Exception as e:
            self.state_var.set("Current state: Error building preview")
            self.error_var.set(f"Last exchange error: {str(e)}")
            print(f"Preview error ({operation}): {e}")

    def mass_edit(self):
        messagebox.showinfo(
            "Массовое редактирование",
            "Пока заглушка.\n\n"
            "Можно доработать: сделать ячейки таблицы редактируемыми "
            "(двойной клик → Entry). Если нужно — скажи, добавлю за 5 минут."
        )


if __name__ == "__main__":
    app = POSConnectorGUI()
    app.root.mainloop()