document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.getElementById("searchForm");
  const searchInput = document.getElementById("searchInput");
  const clearSearchBtn = document.getElementById("clearSearch");
  const searchResults = document.getElementById("searchResults");
  const searchKeyword = document.getElementById("searchKeyword");
  const resultsContent = document.getElementById("resultsContent");
  const noResults = document.getElementById("noResults");
  const categoriesContainer = document.getElementById("categoriesContainer");

  // 搜索功能
  searchForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const query = searchInput.value.trim();

    if (query) {
      // 显示加载状态
      resultsContent.innerHTML =
        '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">正在搜索...</p></div>';
      // searchKeyword.textContent = `"${query}"`; // 删除对 searchKeyword 的依赖

      // 显示搜索结果区域，隐藏分类容器
      categoriesContainer.style.display = "none";
      searchResults.style.display = "block";
      searchResults.style.opacity = "1"; // 确保搜索结果区域可见
      noResults.style.display = "none";

      // 使用Ajax获取搜索结果
      fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          // 清空之前的搜索结果
          resultsContent.innerHTML = "";

          // 设置数量提示到毛玻璃卡片内
          const searchSummary = document.getElementById("searchSummary");
          if (searchSummary) {
            searchSummary.innerHTML = `找到 <strong>${data.count}</strong> 个与 <span class="search-keyword">"${data.keyword}"</span> 相关的网站`;
          }

          if (data.websites && data.websites.length > 0) {
            // 创建卡片容器
            const cardContainer = document.createElement("div");
            cardContainer.className = "card-container";
            resultsContent.appendChild(cardContainer);

            // 循环添加搜索结果
            data.websites.forEach((site) => {
              // 创建卡片元素
              const siteCard = document.createElement("a");
              siteCard.href = `/site/${site.id}`;
              siteCard.className = "site-card";
              siteCard.dataset.id = site.id;
              siteCard.title = site.description || "";
              siteCard.dataset.bsToggle = "tooltip";
              siteCard.dataset.bsPlacement = "bottom";
              siteCard.target = "_blank"; // 添加新标签页打开属性

              // 添加私有标记
              if (site.is_private) {
                const privateBadge = document.createElement("div");
                privateBadge.className = "private-badge";
                privateBadge.title = "私有链接";
                privateBadge.innerHTML = '<i class="bi bi-lock-fill"></i>';
                siteCard.appendChild(privateBadge);
              }

              // 创建网站卡片内容结构
              const siteHeader = document.createElement("div");
              siteHeader.className = "site-header";

              // 创建图标容器
              const iconContainer = document.createElement("div");
              iconContainer.className = "site-icon";

              if (site.icon) {
                const img = document.createElement("img");
                img.src = site.icon;
                img.alt = site.title;
                iconContainer.appendChild(img);
              } else {
                // 使用网站标题首字母作为默认图标
                const defaultIcon = document.createElement("div");
                defaultIcon.className = "default-site-icon";
                defaultIcon.textContent = site.title.charAt(0).toUpperCase();
                iconContainer.appendChild(defaultIcon);
              }

              // 创建文本容器
              const textContainer = document.createElement("div");
              textContainer.className = "site-text";

              const titleEl = document.createElement("h5");
              titleEl.className = "site-title";
              titleEl.textContent = site.title;
              textContainer.appendChild(titleEl);

              const descEl = document.createElement("p");
              descEl.className = "site-description";
              descEl.textContent = site.description || "";
              textContainer.appendChild(descEl);

              // 组装卡片结构
              siteHeader.appendChild(iconContainer);
              siteHeader.appendChild(textContainer);
              siteCard.appendChild(siteHeader);

              // 将卡片添加到结果容器
              cardContainer.appendChild(siteCard);
            });

            // 初始化工具提示
            // if (typeof bootstrap !== "undefined") {
            //   const tooltipTriggerList = [].slice.call(
            //     document.querySelectorAll('[data-bs-toggle="tooltip"]')
            //   );
            //   tooltipTriggerList.map(function (tooltipTriggerEl) {
            //     return new bootstrap.Tooltip(tooltipTriggerEl, {
            //       trigger: "hover",
            //     });
            //   });
            // }

            noResults.style.display = "none";
          } else {
            // 无结果时显示提示
            noResults.style.display = "block";
          }
        })
        .catch((error) => {
          console.error("搜索出错:", error);
          resultsContent.innerHTML =
            '<div class="text-center py-5 text-muted"><i class="bi bi-exclamation-circle fs-1"></i><p class="mt-3">搜索过程中发生错误</p></div>';
        });
    } else {
      clearSearch();
    }
  });

  // 监听搜索框输入
  searchInput.addEventListener("input", function () {
    if (this.value.trim()) {
      clearSearchBtn.style.display = "flex";
    } else {
      clearSearchBtn.style.display = "none";
      // 如果输入框被清空，自动恢复显示原始内容
      if (searchResults.style.display !== "none") {
        clearSearch();
      }
    }
  });

  // 检查初始状态下是否应该显示清除按钮
  function checkClearButtonVisibility() {
    if (searchInput.value.trim()) {
      clearSearchBtn.style.display = "flex";
    } else {
      clearSearchBtn.style.display = "none";
    }
  }

  // 页面加载时和焦点改变时检查
  checkClearButtonVisibility();
  searchInput.addEventListener("focus", checkClearButtonVisibility);

  // 清除搜索按钮
  clearSearchBtn.addEventListener("click", clearSearch);

  // 清除搜索
  function clearSearch() {
    searchInput.value = "";
    clearSearchBtn.style.display = "none";
    searchResults.style.display = "none";
    categoriesContainer.style.display = "block";
    categoriesContainer.style.opacity = "1"; // 确保分类容器可见
  }

  // 监听清除搜索事件
  window.addEventListener("clearSearch", clearSearch);
});
