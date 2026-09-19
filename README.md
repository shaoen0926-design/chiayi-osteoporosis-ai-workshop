# 嘉義醫院｜骨鬆衛教 AI 實作

以骨鬆衛教為簡報主題，讓醫療人員練習資料查證、白話講稿、圖像、NotebookLM、PPT與互動HTML。

包含115題基礎練習、8個整合任務與8份素材。個案和測驗數據為教學用虛構資料；衛教知識附原始來源，內容須經醫療人員審閱。

網站：https://shaoen0926-design.github.io/chiayi-osteoporosis-ai-workshop/

## 維護

教材位於 source/spec.json 與 source/curriculum.json。

```sh
python3 source/build.py
python3 source/validate.py
```

GitHub Pages 由 main 分支根目錄部署。練習進度僅保存在使用者瀏覽器。
