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
        # 1. Початкові факти (сигнали телеметрії)
        self.initial_facts = set()

        # 2. Проміжні факти (агреговані стани)
        self.intermediate_facts = set()

        # 3. Кінцеві висновки та рекомендації
        self.final_decisions = set()

        # 4. Продукційні правила
        self.rules = []

        # 5. Поточний стан робочої пам'яті (ключ -> значення)
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
        # Сортування правил за пріоритетом (від вищого до нижчого)
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

    def run_inference_engine(self, verbose: bool = True):
        """Виклик механізму прямого логічного виведення."""
        engine = ForwardChainingInferenceEngine(self)
        return engine.run_from_existing_memory(verbose=verbose)

    def display_system_state(self):
        """Відображення окремих структур даних бази знань."""
        print("=" * 60)
        print("     ПОТОЧНИЙ СТАН СИСТЕМИ ТА РАЗДІЛЬНИХ СТРУКТУР ЗНАНЬ")
        print("=" * 60)

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
        print("=" * 60)


class ForwardChainingInferenceEngine:

    def __init__(self, knowledge_base: KnowledgeBaseSystem):
        self.kb = knowledge_base

    def run(self, initial_telemetry: dict, verbose: bool = True):
        """Завантажує телеметрію та запускає пряме логічне виведення."""
        self.kb.load_telemetry_facts(initial_telemetry)
        return self.run_from_existing_memory(verbose=verbose)

    def run_from_existing_memory(self, verbose: bool = True):
        """Виконання прямого логічного виведення (Forward Chaining)."""
        executed_rules = set()  # Множина вже активованих правил
        step = 1

        if verbose:
            print("=" * 65)
            print("  ЗАПУСК МЕХАНІЗМУ ПРЯМОГО ЛОГІЧНОГО ВИВЕДЕННЯ (FORWARD CHAINING)")
            print("=" * 65)
            print(
                f"Початкові факти телеметрії: {list(self.kb.initial_facts)}\n"
            )

        # Потоковий цикл прямого виведення
        while True:
            conflict_set = []  # Множина конфліктних правил, умови яких виконуються

            # Аналіз фактів та визначення застосовних правил
            for rule in self.kb.rules:
                if rule.id in executed_rules:
                    continue  # Запобігання повторному спрацьовуванню

                if rule.evaluate(self.kb.working_memory):
                    conflict_set.append(rule)

            # Перевірка умови зупинки
            if not conflict_set:
                if verbose:
                    print(
                        "-> [УМОВА ЗУПИНКИ]: Жодне нове правило не може бути застосоване."
                    )
                break

            # Вирішення конфліктів (правило з max пріоритетом)
            active_rule = conflict_set[0]
            # Активація правила та оновлення робочої пам'яті
            executed_rules.add(active_rule.id)
            new_facts_added = []
            for fact in active_rule.result:
                if not self.kb.working_memory.get(fact, False):
                    self.kb.working_memory[fact] = True
                    new_facts_added.append(fact)

                    # Класифікація висновку
                    if fact in self.kb.known_intermediate:
                        self.kb.intermediate_facts.add(fact)
                    elif fact in self.kb.known_decisions:
                        self.kb.final_decisions.add(fact)

            if verbose:
                print(f"[Крок {step}] Активовано правило: {active_rule.id}")
                print(f"        Умова:  IF {active_rule.condition_str}")
                print(
                    f"        Висновок: THEN {active_rule.result} (Пріоритет: {active_rule.priority})"
                )
                print(f"        Нові факти в пам'яті: {new_facts_added}")
                print("-" * 65)

            step += 1

        if verbose:
            print("\nРЕЗУЛЬТАТИ ВИВЕДЕННЯ:")
            print(
                f"• Згенеровані проміжні факти: {list(self.kb.intermediate_facts)}"
            )
            print(
                f"• Фінальні рішення / рекомендації: {list(self.kb.final_decisions)}"
            )
            print("=" * 65)

        return self.kb.final_decisions


# ДЕМОНСТРАЦІЯ РОБОТИ
if __name__ == "__main__":
    kb = KnowledgeBaseSystem()
    engine = ForwardChainingInferenceEngine(kb)
    # Вхідні дані телеметрії
    input_telemetry = {
        "bsod_occurred": True,
        "ram_usage_high": True,
        "cpu_load_high": True,
        "backup_created": False,
    }
    # Виконання виведення
    engine.run(input_telemetry, verbose=True)
    # Відображення підсумкового стану бази знань
    kb.display_system_state()