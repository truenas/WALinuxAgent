from dungeon_crawler.constants import CHINA_CLOUD, IMAGE_NAME, CLOUD
from dungeon_crawler.scenarios.interfaces import BaseExtensionTestClass
from tank.unique import Unique


class TestClass(BaseExtensionTestClass):

    def __init__(self, metadata):
        super(TestClass, self).__init__(metadata)
        storage_manager = self.resource_group_manager.storage_manager
        self.storage_account_name = 'agentbvt{0}'.format(Unique.unique(8))
        storage_manager.create_storage_account(self.storage_account_name)
        self.storage_keys = storage_manager.get_storage_keys(self.storage_account_name)
        self.storage_sas_token = storage_manager.get_sas_token(self.storage_account_name,
                                                               self.storage_keys['key1'])

    @property
    def is_unsupported(self) -> bool:
        if self.metadata[IMAGE_NAME] == "suse_12" and self.metadata[CLOUD].name == CHINA_CLOUD:
            self.logger.info("This test is disabled for suse_12 in MC as LAD has missing dependencies there.")
            return True
        return False

    def get_extension_tuple_list(self):
        ext_name = 'LinuxDiagnostic3.0'
        ext_type = 'LinuxDiagnostic'
        publisher = 'Microsoft.Azure.Diagnostics'
        ext_version = '3.0'
        protected_settings = {
            'storageAccountName': self.storage_account_name,
            'storageAccountSasToken': self.storage_sas_token
        }
        ext_prop = self.create_vm_extension_properties(publisher=publisher,
                                                       extension_type=ext_type,
                                                       version=ext_version,
                                                       protected_settings=protected_settings,
                                                       allow_auto_upgrade_minor_version=True)

        return [(ext_name, ext_prop)]
