SELECT 
    asset_class_id as db_asset_class_id,
    asset_class_name as db_asset_class_name,
    asset_type_id as db_asset_type_id,
    asset_type_name as db_asset_type_name,
    sub_asset_type_id as db_sub_asset_type_id,
    sub_asset_type_name as db_sub_asset_type_name
FROM public."AssetClassification" WHERE asset_classification_id={{created_classification_id}};