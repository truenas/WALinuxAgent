from dungeon_crawler.scenarios.interfaces import BaseExtensionTestClass
from tank.unique import Unique


class TestClass(BaseExtensionTestClass):

    def __init__(self, metadata):
        super(TestClass, self).__init__(metadata)
        storage_manager = self.resource_group_manager.storage_manager
        self.storage_account_name = 'agentbvt{0}'.format(Unique.unique(8))
        storage_manager.create_storage_account(self.storage_account_name)
        self.storage_keys = storage_manager.get_storage_keys(self.storage_account_name)

    def get_extension_tuple_list(self):
        ext_name = 'LinuxDiagnostic2.3'
        publisher = 'Microsoft.OSTCExtensions'
        ext_type = 'LinuxDiagnostic'
        ext_version = '2.3'
        protected_settings = {'storageAccountName': self.storage_account_name,
                              'storageAccountKey': self.storage_keys['key1']}
        settings = {'enableSyslog': 'false'}

        ext_prop_1 = self.create_vm_extension_properties(publisher=publisher,
                                                         extension_type=ext_type,
                                                         version=ext_version,
                                                         protected_settings=protected_settings,
                                                         allow_auto_upgrade_minor_version=False)

        ext_prop_2 = self.create_vm_extension_properties(publisher=publisher,
                                                         extension_type=ext_type,
                                                         version=ext_version,
                                                         settings=settings,
                                                         allow_auto_upgrade_minor_version=False)

        return [(ext_name, ext_prop_1), (ext_name, ext_prop_2)]
