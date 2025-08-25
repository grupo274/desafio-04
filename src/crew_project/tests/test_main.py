# 1. Verificar ambiente

from crew_project.tests.check_environment import check_environment

from crew_project.tests.test_config import test_config, test_config_loading   
# Tools
#from crew_project.tests.test_excel_tool import test_excel_tool
#from crew_project.tests.test_rules_api_tool import test_rules_api_tool
#from crew_project.tests.test_dataframe_tools import test_dataframe_tools

#from crew_project.tests.test_sistema_completo import test_sistema_completo

#from crew_project.tests.test_execucao_real import test_execucao_real

check_environment()
test_config_loading()

