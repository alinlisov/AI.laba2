import json
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
        }

    def _init_rules(self):
        self.rules = [
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
                "R11",
                lambda m: m.get("memory_fault") and m.get("cpu_load_high"),
                "memory_fault AND cpu_load_high",
                ["isolate_node", "migrate_services"],
                90,
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

class ForwardChainingWithExplanation:
    """Механізм прямого виведення з інтегрованим модулем пояснень."""
    def __init__(self, knowledge_base: KnowledgeBaseSystem):
        self.kb = knowledge_base
        self.explanation_trace = []  # Буфер зберігання історії виведення

    def run(self, initial_telemetry: dict):
        """Виконання виведення із фіксацією кроків у трасувальному буфері."""
        self.kb.load_telemetry_facts(initial_telemetry)
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
            # Вирішення конфліктів за пріоритетом
            active_rule = conflict_set[0]
            executed_rules.add(active_rule.id)
            new_facts_added = []
            for fact in active_rule.result:
                if not self.kb.working_memory.get(fact, False):
                    self.kb.working_memory[fact] = True
                    new_facts_added.append(fact)

                    if fact in self.kb.known_intermediate:
                        self.kb.intermediate_facts.add(fact)
                    elif fact in self.kb.known_decisions:
                        self.kb.final_decisions.add(fact)

            # Реєстрація детального кроку для модуля пояснень
            self.explanation_trace.append(
                {
                    "step": step,
                    "rule_id": active_rule.id,
                    "priority": active_rule.priority,
                    "condition": active_rule.condition_str,
                    "result": active_rule.result,
                    "new_facts": new_facts_added,
                }
            )

            step += 1
        return self.kb.final_decisions
    def explain_decision(self):
        """Формування та виведення звіту про прийняте рішення."""
        print(" " * 65)
        print("        ПОЯСНЕННЯ ОТРИМАНОГО РІШЕННЯ")
        print(" " * 65)
        print(f"1. Вхідні початкові факти: {list(self.kb.initial_facts)}\n")
        print("2. Ланцюжок логічних висновків (послідовність правил):")
        for step_info in self.explanation_trace:
            print(
                f"   [Крок {step_info['step']}] Правило {step_info['rule_id']} (Пріоритет P={step_info['priority']})"
            )
            print(f"      • На основі умови : IF {step_info['condition']}")
            print(f"      • Сформовано висновок: THEN {step_info['result']}")
            print(f"      • Додано нові факти  : {step_info['new_facts']}")
            print("   " + "-" * 55)

        print("\n3. Підсумковий результат:")
        print(f"   • Проміжні стани : {list(self.kb.intermediate_facts)}")
        print(f"   • Кінцеві рішення : {list(self.kb.final_decisions)}")

# ДЕМОНСТРАЦІЯ
if __name__ == "__main__":
    kb = KnowledgeBaseSystem()
    engine = ForwardChainingWithExplanation(kb)
    telemetry_data = {
        "bsod_occurred": True,
        "ram_usage_high": True,
        "cpu_load_high": True,
    }
    # Запуск алгоритму виведення
    engine.run(telemetry_data)
    engine.explain_decision()