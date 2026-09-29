class ProductionRule:

    def __init__(self, rule_id, condition_func, condition_str, result, priority):
        self.id = rule_id
        self.condition_func = condition_func
        self.condition_str = condition_str
        self.result = result
        self.priority = priority

    def evaluate(self, memory):
        try:
            return self.condition_func(memory)
        except KeyError:
            return False


class KnowledgeBaseSystem:

    def __init__(self):
        self.initial_facts = set()
        self.intermediate_facts = set()
        self.final_decisions = set()
        self.rules = []
        self.working_memory = {}

        self.available_telemetry = {
            "1": ("cpu_temp_high", "Висока температура процесора (CPU)"),
            "2": ("fan_speed_low", "Низькі оберти вентилятора"),
            "3": ("bsod_occurred", "Критичний збій системи (BSOD/Panic)"),
            "4": ("ram_usage_high", "Високе використання оперативної пам'яті"),
            "5": ("cpu_load_high", "Високе завантаження процесора (CPU Load)"),
            "6": ("drive_smart_bad", "Помилки диска в SMART"),
            "7": ("read_write_errors", "Помилки читання/запису на накопичувач"),
            "8": ("backup_created", "Резервна копія створена успішно"),
        }

        self._init_fact_categories()
        self._init_rules()

    def _init_fact_categories(self):
        self.known_intermediate = {
            "fan_failure",
            "thermal_paste_degradation",
            "system_instability",
            "memory_fault",
            "storage_degradation",
        }
        self.known_decisions = {
            "check_cooling_system",
            "emergency_shutdown",
            "run_memtest_diagnostic",
            "isolate_node",
            "migrate_services",
            "immediate_backup",
            "replace_drive",
            "replace_thermal_paste",
        }

    def _init_rules(self):
        self.rules = [
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
                lambda m: m.get("bsod_occurred"),
                "bsod_occurred",
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
            ProductionRule(
                "R12",
                lambda m: m.get("fan_failure"),
                "fan_failure",
                ["check_cooling_system"],
                70,
            ),
            ProductionRule(
                "R13",
                lambda m: m.get("thermal_paste_degradation"),
                "thermal_paste_degradation",
                ["replace_thermal_paste"],
                65,
            ),
            ProductionRule(
                "R14",
                lambda m: m.get("memory_fault"),
                "memory_fault",
                ["run_memtest_diagnostic"],
                65,
            ),
        ]
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def load_telemetry_facts(self, telemetry_data: dict):
        self.working_memory.clear()
        self.initial_facts.clear()
        self.intermediate_facts.clear()
        self.final_decisions.clear()

        for fact, val in telemetry_data.items():
            if val:
                self.working_memory[fact] = True
                self.initial_facts.add(fact)


class InferenceEngineWithUI:

    def __init__(self, kb: KnowledgeBaseSystem):
        self.kb = kb
        self.explanation_trace = []

    def run_inference(self):
        self.explanation_trace.clear()
        executed_rules = set()
        step = 1

        while True:
            conflict_set = []
            for rule in self.kb.rules:
                if rule.id in executed_rules:
                    continue
                if rule.evaluate(self.kb.working_memory):
                    conflict_set.append(rule)

            if not conflict_set:
                break

            active_rule = conflict_set[0]
            executed_rules.add(active_rule.id)

            new_facts = []
            for fact in active_rule.result:
                if not self.kb.working_memory.get(fact, False):
                    self.kb.working_memory[fact] = True
                    new_facts.append(fact)

                    if fact in self.kb.known_intermediate:
                        self.kb.intermediate_facts.add(fact)
                    elif fact in self.kb.known_decisions:
                        self.kb.final_decisions.add(fact)

            self.explanation_trace.append(
                {
                    "step": step,
                    "rule_id": active_rule.id,
                    "priority": active_rule.priority,
                    "condition": active_rule.condition_str,
                    "result": active_rule.result,
                    "new_facts": new_facts,
                }
            )
            step += 1


class ExpertSystemUI:

    def __init__(self):
        self.kb = KnowledgeBaseSystem()
        self.engine = InferenceEngineWithUI(self.kb)

    def display_header(self):
        print("\n" + "=" * 70)
        print("    ЕКСПЕРТНА СИСТЕМА ДІАГНОСТИКИ СЕРВЕРНОГО ОБЛАДНАННЯ")
        print("=" * 70)

    def select_initial_facts(self) -> dict:
        print("\n[Крок 1] Оберіть наявні симптоми/сигнали телеметрії:")
        print("-" * 50)

        for key, (fact_code, description) in self.kb.available_telemetry.items():
            print(f"  [{key}] {description} ({fact_code})")

        print("-" * 50)
        user_input = input(
            "Введіть номери обраних симптомів через кому (наприклад, 1,2,5): "
        )

        selected_keys = [k.strip() for k in user_input.split(",") if k.strip()]
        selected_telemetry = {}

        for key, (fact_code, _) in self.kb.available_telemetry.items():
            selected_telemetry[fact_code] = key in selected_keys

        return selected_telemetry

    def render_results(self):
        print("\n" + "=" * 70)
        print("                    РЕЗУЛЬТАТИ ДІАГНОСТИКИ")
        print("=" * 70)

        print("\n1. ОБРАНІ ПОЧАТКОВІ ФАКТИ:")
        if self.kb.initial_facts:
            for f in self.kb.initial_facts:
                print(f"   • {f}")
        else:
            print("   (жодного факту не обрано)")

        print("\n2. ЛАНЦЮЖОК ЛОГІЧНОГО ВИВЕДЕННЯ (ТРАСУВАННЯ):")
        if self.engine.explanation_trace:
            for step in self.engine.explanation_trace:
                print(
                    f"   [Крок {step['step']}] Правило {step['rule_id']} (P={step['priority']})"
                )
                print(f"      - Умова  : IF {step['condition']}")
                print(f"      - Висновок: THEN {step['result']}")
                print(f"      - Нові факти: {step['new_facts']}")
                print("   " + "-" * 45)
        else:
            print("   (ланцюжок порожній — жодне правило не спрацювало)")

        print("\n3. СФОРМОВАНІ РІШЕННЯ ТА РЕКОМЕНДАЦІЇ:")
        if self.kb.final_decisions:
            for decision in self.kb.final_decisions:
                print(f"   >>> [РЕКОМЕНДАЦІЯ] -> {decision.upper()} <<<")
        else:
            print("   [i] Критичних відхилень не виявлено або недостатньо даних.")

        print("=" * 70)

    def start_session(self):
        while True:
            self.display_header()
            print("\nГОЛОВНЕ МЕНЮ:")
            print("  1. Запустити нову діагностику")
            print("  2. Вийти з системи")

            choice = input("\nОберіть дію (1-2): ").strip()

            if choice == "1":
                telemetry_data = self.select_initial_facts()
                self.kb.load_telemetry_facts(telemetry_data)

                print("\n[...] Виконується логічне виведення (Forward Chaining)...")
                self.engine.run_inference()

                self.render_results()

                input("\nНатисніть Enter, щоб повернутися в меню...")
            elif choice == "2":
                print("\nЗавершення роботи системи. До побачення!")
                break
            else:
                print("\n[!] Некоректний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    ui = ExpertSystemUI()
    ui.start_session()