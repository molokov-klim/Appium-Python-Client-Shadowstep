# shadowstep/page_object/page_object_extractor.py

class PageObjectRecyclerExplorer:
    """Скроллит внутри scrollable-контейнера (recycler), ищет новые элементы и готовит их для PageObject.

    Этот класс используется в рантайме. Он прокручивает указанный контейнер (например, RecyclerView),
    вытаскивает элементы, которые ещё не были найдены, и возвращает их в формате, совместимом с PageObjectExtractor.

    Зачем нужен:
        - работает через `self.base.scroll_down()` (лениво);
        - после каждого скролла парсит XML и находит новые элементы;
        - фильтрует элементы по принадлежности к `recycler_id`;
        - удаляет дубликаты (по resource_id, text, content_desc);
        - возвращает список новых элементов (dict-ов), которые потом можно передать в генератор.

    Пример использования:
        explorer = RecyclerExplorer(driver_proxy)
        elements = explorer.scroll_and_collect(recycler_id="recycler_view", max_scrolls=10)

    Возвращает:
        List[dict]: список новых элементов из recycler-контейнера.
    """
