import json
class ProductionRule:
    def __init__(self, rule_id, condition_func, condition_str, result, priority):
        self.id = rule_id
        self.condition_func = condition_func  # Лямбда-функція для перевірки
        self.condition_str = condition_str  # Текстовий опис умови
        self.result = result  # Новий факт чи список фактів
        self.priority = priority  # Пріоритет (P)
    def evaluate(self, memory):
        """Перевірка виконання умови правила на поточній робочій пам'яті."""
        try:
            return self.condition_func(memory)
        except KeyError:
            return False

class KnowledgeBaseSystem:
    def __init__(self):
        # 1. Початкові факти
        self.initial_facts = set()
        # 2. Проміжні факти
        self.intermediate_facts = set()
        # 3. Кінцеві висновки
        self.final_decisions = set()
        # 4. Продукційні правила
        self.rules = []
        # 5. Поточний стан робочої пам'яті
        self.working_memory = {}
        # Реєстрація визначених категорій фактів для класифікації
        self._init_fact_categories()
        self._init_rules()

    def _init_fact_categories(self):
        """Реєстрація типів фактів для автоматичного розділення."""
        self.known_intermediate = {
            "fan_failure",
            "thermal_paste_degradation",
            "system_instability",
            "memory_fault",
            "storage_degradation",
            "storage_overflow",
            "network_bottleneck",
            "resource_exhaustion",
        }
        self.known_decisions = {
            "check_cooling_system",
            "emergency_shutdown",
            "replace_thermal_paste",
            "run_memtest_diagnostic",
            "isolate_node",
            "migrate_services",
            "immediate_backup",
            "replace_drive",
            "clean_temp_files",
            "expand_disk_volume",
            "check_router_and_cables",
            "scale_server_resources",
            "check_background_processes",
            "block_ip_and_notify_admin",
        }
    def _init_rules(self):
        """Ініціалізація продукційних правил з пріоритетами."""
        self.rules = [
            # Проміжні факти (Правила 1-8)
            ProductionRule(
                "R1",
                lambda m: m.get("cpu_temp_high") and m.get("fan_speed_low"),
                "cpu_temp_high AND fan_speed_low",
                ["fan_failure"],
                85,
            ),
            ProductionRule(
                "R2",
                lambda m: m.get("cpu_temp_high")
                and not m.get("fan_speed_low"),
                "cpu_temp_high AND NOT fan_speed_low",
                ["thermal_paste_degradation"],
                70,
            ),
            ProductionRule(
                "R3",
                lambda m: m.get("bsod_occurred") or m.get("kernel_panic_logged"),
                "bsod_occurred OR kernel_panic_logged",
                ["system_instability"],
                80,
            ),
            ProductionRule(
                "R4",
                lambda m: m.get("ram_usage_high")
                and m.get("system_instability"),
                "ram_usage_high AND system_instability",
                ["memory_fault"],
                85,
            ),
            ProductionRule(
                "R5",
                lambda m: m.get("drive_smart_bad")
                or m.get("read_write_errors"),
                "drive_smart_bad OR read_write_errors",
                ["storage_degradation"],
                90,
            ),
            # Критичні рішення (Правила 9-11)
            ProductionRule(
                "R9",
                lambda m: m.get("fan_failure") and m.get("cpu_load_high"),
                "fan_failure AND cpu_load_high",
                ["emergency_shutdown"],
                100,
            ),
            ProductionRule(
                "R10",
                lambda m: m.get("storage_degradation")
                and not m.get("backup_created"),
                "storage_degradation AND NOT backup_created",
                ["immediate_backup", "replace_drive"],
                95,
            ),
            ProductionRule(
                "R11",
                lambda m: m.get("memory_fault") and m.get("cpu_load_high"),
                "memory_fault AND cpu_load_high",
                ["isolate_node", "migrate_services"],
                90,
            ),
            # Стандартні рішення (Правила 12-14)
            ProductionRule(
                "R12",
                lambda m: m.get("fan_failure"),
                "fan_failure",
                ["check_cooling_system"],
                70,
            ),
            ProductionRule(
                "R14",
                lambda m: m.get("memory_fault"),
                "memory_fault",
                ["run_memtest_diagnostic"],
                65,
            ),
        ]
        # Сортування правил за пріоритетом
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    def load_telemetry_facts(self, telemetry_data: dict):
        """Завантаження початкових фактів у робочу пам'ять."""
        self.working_memory.clear()
        self.initial_facts.clear()
        self.intermediate_facts.clear()
        self.final_decisions.clear()
        for fact, val in telemetry_data.items():
            if val:
                self.working_memory[fact] = True
                self.initial_facts.add(fact)

    def run_inference_engine(self):
        """Пряме логічне виведення (Forward Chaining) з урахуванням пріоритетів."""
        executed_rules = set()
        while True:
            rule_fired = False

            for rule in self.rules:
                if rule.id in executed_rules:
                    continue

                if rule.evaluate(self.working_memory):
                    # Активація правила
                    executed_rules.add(rule.id)
                    rule_fired = True
                    # Додавання висновків до робочої пам'яті
                    for fact in rule.result:
                        self.working_memory[fact] = True

                        if fact in self.known_intermediate:
                            self.intermediate_facts.add(fact)
                        elif fact in self.known_decisions:
                            self.final_decisions.add(fact)

                    # Зупиняємо поточний прохід і повертаємось на початок
                    break
            if not rule_fired:
                break

    def display_system_state(self):
        """Відображення окремих структур даних бази знань."""
        print("     ПОТОЧНИЙ СТАН СИСТЕМИ ТА РАЗДІЛЬНИХ СТРУКТУР ЗНАНЬ")
        print(" " * 60)
        print("\n1. ПОЧАТКОВІ ФАКТИ (Телеметрія):")
        for f in self.initial_facts:
            print(f"   • {f}")
        print("\n2. ПРОМІЖНІ ФАКТИ (Агреговані стани):")
        if self.intermediate_facts:
            for f in self.intermediate_facts:
                print(f"   • {f}")
        else:
            print("   (відсутні)")

        print("\n3. КІНЦЕВІ ВИСНОВКИ ТА РЕКОМЕНДАЦІЇ:")
        if self.final_decisions:
            for d in self.final_decisions:
                print(f"   • [РЕКОМЕНДАЦІЯ] -> {d}")
        else:
            print("   (відсутні)")

        print("\n4. ПРИКЛАД ЗБЕРЕЖЕНИХ ПРОДУКЦІЙНИХ ПРАВИЛ (Топ-3 за пріоритетом):")
        for r in self.rules[:3]:
            print(
                f"   • [{r.id}] (P={r.priority}) IF {r.condition_str} THEN {r.result}"
            )
        print("\n5. ПОВНИЙ ПОТОЧНИЙ СТАН РОБОЧОЇ ПАМ'ЯТІ:")
        print("  ", json.dumps(self.working_memory, indent=4))

# ДЕМОНСТРАЦІЯ РОБОТИ ПРОГРАМИ
if __name__ == "__main__":
    kb = KnowledgeBaseSystem()
    # Початковий набір вхідних фактів для багатокрокового виведення
    input_telemetry = {
        "bsod_occurred": True,
        "ram_usage_high": True,
        "cpu_load_high": True,
        "backup_created": False,
    }
    print("Завантаження вхідної телеметрії...")
    kb.load_telemetry_facts(input_telemetry)
    print("Запуск машинно-логічного виведення (Forward Chaining)...")
    kb.run_inference_engine()
    # Вивід результатів
    kb.display_system_state()