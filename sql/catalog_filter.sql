-- Catalog filter (dynamic year via $(vYear_Dynamic))
where
(
		(
			catalog_name <> 'Custom Kit' and catalog_type_description<>'Toys To Grow On'
			and MATCH(catalog_bart_catype,'EL','P','PT','IT') and catalog_page <520 and not isnull(catalog_section)
			and  NOT isnull(catalog_item_page_sqmm)
		)
		OR (catalog_year >= 2026 and MATCH(catalog_bart_catype,'EL','P','PT','IT') and catalog_type_description<>'Toys To Grow On')
and NOT isnull(catalog_item_page_sqmm))
and catalog_year>= $(vYear_Dynamic)
