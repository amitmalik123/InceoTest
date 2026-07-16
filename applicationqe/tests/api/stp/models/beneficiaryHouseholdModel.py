from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class AccountHolder:
    id: str
    fullName: str
    registrationType: Optional[str]
    masked_ssn: str
    accountStatus: Optional[str]
    accountOpenDate: Optional[str]
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'AccountHolder':
        return AccountHolder(
            id=data.get('id', ''),
            fullName=data.get('fullName', ''),
            registrationType=data.get('registrationType'),
            masked_ssn=data.get('masked_ssn', ''),
            accountStatus=data.get('accountStatus'),
            accountOpenDate=data.get('accountOpenDate')
        )


@dataclass
class Meta:
    totalAccountHolders: int
    householdName: str
    advisorName: str
    lastUpdated: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Meta':
        return Meta(
            totalAccountHolders=data.get('totalAccountHolders', 0),
            householdName=data.get('householdName', ''),
            advisorName=data.get('advisorName', ''),
            lastUpdated=data.get('lastUpdated', '')
        )


@dataclass
class DataSource:
    accountHolders: List[AccountHolder]
    meta: Meta
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'DataSource':
        account_holders_data = data.get('accounts.parties.accountHolders', [])
        account_holders = [AccountHolder.from_json(holder) for holder in account_holders_data]
        
        meta_data = data.get('meta', {})
        meta = Meta.from_json(meta_data)
        
        return DataSource(
            accountHolders=account_holders,
            meta=meta
        )


@dataclass
class BeneficiaryHouseholdModel:
    householdDisplayName: str
    schema: Dict[str, Any]
    dataSource: DataSource
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'BeneficiaryHouseholdModel':
        household_display_name = data.get('householdDisplayName', '')
        schema = data.get('schema', {})
        
        data_source_data = data.get('dataSource', {})
        data_source = DataSource.from_json(data_source_data)
        
        return BeneficiaryHouseholdModel(
            householdDisplayName=household_display_name,
            schema=schema,
            dataSource=data_source
        )
    
    def get_account_holder_count(self) -> int:
        return len(self.dataSource.accountHolders)
    
    def get_household_name(self) -> str:
        return self.dataSource.meta.householdName
    
    def get_account_holder_by_name(self, name: str) -> Optional[AccountHolder]:
        for holder in self.dataSource.accountHolders:
            if holder.fullName == name:
                return holder
        return None
