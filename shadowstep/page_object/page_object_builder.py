# shadowstep/page_object/page_object_builder.py

class PageObjectBuilder:
    """Управляет полным процессом генерации PageObject: от XML до динамически найденных элементов.

    Это оркестратор, который объединяет:
        - PageObjectExtractor — чтобы разобрать XML;
        - PageObjectGenerator — чтобы сгенерировать Python-код;
        - RecyclerExplorer — чтобы найти элементы, появляющиеся только при скролле.

    Зачем нужен:
        - сначала вызвать `generate_initial(xml)` — сгенерировать базовые элементы;
        - потом вызвать `discover_recycler("recycler_id")` — найти недостающие элементы внутри скролла;
        - в конце вызвать `combine_all()` — объединить всё в итоговый класс PageObject.

    Расширяемость:
        - можно будет сохранять/загружать список элементов через JSON;
        - можно будет делить на секции (header/body/footer);
        - можно добавить режим "append" и разрешение конфликтов с ручным кодом.

    Пример:
        builder = PageObjectBuilder("LoginPage", driver_proxy)
        builder.generate_initial(xml)
        builder.discover_recycler("recycler_view_id")
        builder.combine_all()
    """
