# test_config.py
from crew_project.crew import agents, tasks, crew

def test_config_loading():
    print("=== Teste Configurações ===")
    
    # Teste agents
    print(f"✅ Agents carregados: {len(agents)}")
    for name, agent in agents.items():
        print(f"  🤖 {name}: {agent.role}")
        print(f"     Tools: {len(agent.tools)}")
    
    print()
    
    # Teste tasks  
    print(f"✅ Tasks carregadas: {len(tasks)}")
    for name, task in tasks.items():
        print(f"  📋 {name}: {task.agent.role}")
    
    print()
    
    # Teste crew
    print(f"✅ Crew configurado:")
    print(f"  Agents: {len(crew.agents)}")
    print(f"  Tasks: {len(crew.tasks)}")
    print(f"  Process: {crew.process}")

if __name__ == "__main__":
    test_config_loading()