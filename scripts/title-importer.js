/**
 * Title Import Component
 * Allows importing titles from NotebookLM and adding them to publications
 */

const TitleImporter = (function () {
    let modalElement = null;
    let searchIndex = [];
    let foundArticles = [];
    let lastResults = [];

    const styles = `
        .title-import-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(26, 32, 44, 0.4);
            backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10001;
            animation: titleImportFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes titleImportFadeIn {
            from { opacity: 0; transform: scale(0.98); }
            to { opacity: 1; transform: scale(1); }
        }

        .title-import-window {
            background: #ffffff;
            border-radius: 16px;
            width: 95%;
            max-width: 720px;
            max-height: 85vh;
            overflow: hidden;
            box-shadow: 
                0 20px 25px -5px rgba(0, 0, 0, 0.1), 
                0 10px 10px -5px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            font-family: 'Inter', -apple-system, sans-serif;
            border: 1px solid rgba(0,0,0,0.05);
        }

        .title-import-header {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #ffffff;
        }

        .title-import-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1a202c;
            margin: 0;
            letter-spacing: -0.025em;
        }

        .title-import-close {
            background: transparent;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #a0aec0;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s;
        }

        .title-import-close:hover {
            background: #f7fafc;
            color: #4a5568;
        }

        .title-import-body {
            padding: 2rem;
            overflow-y: auto;
            flex: 1;
        }

        .title-import-instructions {
            background: #f8fafc;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
            color: #4a5568;
            line-height: 1.6;
            border: 1px solid #e2e8f0;
        }

        .title-import-textarea {
            width: 100%;
            height: 180px;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            padding: 1rem;
            font-size: 1rem;
            resize: vertical;
            font-family: 'Inter', monospace;
            transition: all 0.2s;
            background: #ffffff;
            color: #2d3748;
            line-height: 1.6;
        }

        .title-import-textarea:focus {
            outline: none;
            border-color: #4a5568;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }

        .title-import-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            letter-spacing: 0.01em;
            height: 48px; /* Fixed height for alignment */
        }

        .title-import-btn-primary {
            background: #2d3748;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .title-import-btn-primary:hover {
            background: #1a202c;
            transform: translateY(-1px);
        }

        .title-import-btn-secondary {
            background: white;
            color: #4a5568;
            border: 1px solid #cbd5e0;
        }
        
        .title-import-btn-secondary:hover {
            background: #f7fafc;
            border-color: #a0aec0;
            color: #2d3748;
        }

        .title-import-results {
            margin-top: 2rem;
        }

        .title-import-stats {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
            flex-wrap: wrap;
        }

        .title-import-stat {
            padding: 0.4rem 1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .title-import-stat.success {
            background: #def7ec;
            color: #03543f;
        }

        .title-import-stat.warning {
            background: #fdf6b2;
            color: #723b13;
        }

        .title-import-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #fafafa;
        }

        .title-import-item {
            display: flex;
            align-items: flex-start;
            padding: 1rem;
            border-bottom: 1px solid #edf2f7;
            gap: 1rem;
            background: white;
        }

        .title-import-item:last-child {
            border-bottom: none;
        }

        .title-import-item.found {
            cursor: pointer;
            transition: background 0.2s;
        }

        .title-import-item.found:hover {
            background: #f8fafc;
        }
        
        .title-import-item.not-found {
            background: #fff5f5;
        }

        .title-import-item-icon {
            font-size: 1.1rem;
            line-height: 1;
            margin-top: 0.1rem;
            color: #48bb78;
        }
        
        .title-import-item.not-found .title-import-item-icon {
            color: #f56565;
        }

        .title-import-item-text {
            flex: 1;
            min-width: 0;
        }

        .title-import-item-title {
            font-weight: 500;
            color: #2d3748;
            font-size: 0.95rem;
            line-height: 1.4;
            margin-bottom: 0.25rem;
        }

        .title-import-item-category {
            font-size: 0.75rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .title-import-actions {
            padding: 1.5rem 2rem;
            border-top: 1px solid #f1f5f9;
            display: flex;
            justify-content: flex-end;
            align-items: center; /* Ensures vertical alignment */
            gap: 1rem;
            background: #ffffff;
            flex-wrap: wrap;
        }

        .title-import-pub-select {
            height: 48px; /* Fixed height matches buttons */
            padding: 0 1rem;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            font-size: 0.95rem;
            min-width: 240px;
            flex: 1;
            max-width: 320px;
            color: #2d3748;
            background-color: white;
            cursor: pointer;
            transition: all 0.2s;
        }

        .title-import-pub-select:focus {
            outline: none;
            border-color: #4a5568;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }

        .title-import-article-preview {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 650px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            z-index: 10002;
            animation: titleImportFadeIn 0.2s ease-out;
            font-family: 'Inter', -apple-system, sans-serif;
        }

        .title-import-preview-header {
            padding: 1.5rem 2rem;
            background: #ffffff;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .title-import-preview-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1a202c;
            margin: 0;
            line-height: 1.3;
        }

        .title-import-preview-meta {
            font-size: 0.85rem;
            color: #718096;
            margin-top: 0.5rem;
            font-weight: 500;
        }

        .title-import-preview-body {
            padding: 2rem;
            line-height: 1.8;
            color: #4a5568;
            font-size: 1rem;
        }

        .title-import-preview-link {
            display: inline-block;
            margin-top: 1.5rem;
            color: #2d3748;
            text-decoration: none;
            font-weight: 600;
            border-bottom: 1px solid #cbd5e0;
            padding-bottom: 2px;
            transition: all 0.2s;
        }

        .title-import-preview-link:hover {
            color: #000;
            border-color: #000;
        }
    `;

    function injectStyles() {
        if (document.getElementById('title-import-styles')) return;
        const styleEl = document.createElement('style');
        styleEl.id = 'title-import-styles';
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
    }

    async function loadSearchIndex() {
        if (searchIndex.length > 0) return;

        const paths = [
            'Data/advanced_search_index.json',
            './Data/advanced_search_index.json',
            '../Data/advanced_search_index.json'
        ];

        for (const path of paths) {
            try {
                const response = await fetch(path);
                if (response.ok) {
                    searchIndex = await response.json();
                    console.log(`TitleImporter: Loaded ${searchIndex.length} teachings`);
                    return;
                }
            } catch (e) {
                console.log(`TitleImporter: Could not load from ${path}`);
            }
        }
    }

    function normalizeText(text) {
        return text
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[•\-–—]/g, '')
            .replace(/^\d+\.\s*/, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function findMatch(title) {
        const normalizedTitle = normalizeText(title);
        if (!normalizedTitle || normalizedTitle.length < 5) return null;

        // Exact match
        let match = searchIndex.find(item =>
            normalizeText(item.title) === normalizedTitle
        );
        if (match) return match;

        // Contains match
        match = searchIndex.find(item => {
            const normalizedItemTitle = normalizeText(item.title);
            return normalizedItemTitle.includes(normalizedTitle) ||
                normalizedTitle.includes(normalizedItemTitle);
        });
        if (match) return match;

        // Fuzzy match (first 25 characters)
        const shortTitle = normalizedTitle.substring(0, 25);
        match = searchIndex.find(item => {
            const normalizedItemTitle = normalizeText(item.title);
            return normalizedItemTitle.startsWith(shortTitle) ||
                shortTitle.startsWith(normalizedItemTitle.substring(0, 25));
        });
        return match;
    }

    function searchTitles(inputText) {
        const lines = inputText.split('\n').filter(line => line.trim());
        foundArticles = [];
        const results = [];

        lines.forEach(line => {
            const cleanLine = line.replace(/^[•\-–—\d.)\s]+/, '').trim();
            if (!cleanLine || cleanLine.length < 3) return;

            const match = findMatch(cleanLine);

            if (match) {
                foundArticles.push(match);
                results.push({
                    found: true,
                    original: cleanLine,
                    article: match
                });
            } else {
                results.push({
                    found: false,
                    original: cleanLine
                });
            }
        });

        return results;
    }

    function renderResults(results) {
        // Store for preview access
        lastResults = results;

        const container = document.getElementById('titleImportResults');
        if (!container) return;

        const foundCount = results.filter(r => r.found).length;
        const notFoundCount = results.filter(r => !r.found).length;

        let html = `
            <div class="title-import-stats">
                <span class="title-import-stat success">✓ ${foundCount} encontrado(s)</span>
                <span class="title-import-stat warning">⚠ ${notFoundCount} não encontrado(s)</span>
            </div>
            <div class="title-import-list">
        `;

        results.forEach((result, index) => {
            if (result.found) {
                html += `
                    <div class="title-import-item found" onclick="TitleImporter.showPreview(${index})" title="Clique para ver detalhes">
                        <span class="title-import-item-icon">✓</span>
                        <div class="title-import-item-text">
                            <div class="title-import-item-title">${result.article.title}</div>
                            <div class="title-import-item-category">${result.article.category || ''}</div>
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="title-import-item not-found">
                        <span class="title-import-item-icon">⚠</span>
                        <div class="title-import-item-text">
                            <div class="title-import-item-title">${result.original}</div>
                            <div class="title-import-item-category">Título não encontrado</div>
                        </div>
                    </div>
                `;
            }
        });

        html += '</div>';
        container.innerHTML = html;

        // Show add button if there are results
        const actionsDiv = document.getElementById('titleImportActions');
        if (actionsDiv && foundArticles.length > 0) {
            actionsDiv.style.display = 'flex';
            renderPublicationSelect();
        }
    }

    function renderPublicationSelect() {
        const container = document.getElementById('pubSelectContainer');
        if (!container) return;

        const publications = FavoritesManager.getPublications();
        const pubList = Object.values(publications);

        let html = `<select id="targetPubSelect" class="title-import-pub-select">
            <option value="">-- Selecione uma publicação --</option>
            <option value="__NEW__">+ Criar nova publicação...</option>
        `;

        pubList.forEach(pub => {
            html += `<option value="${pub.id}">${pub.name} (${pub.items.length} artigos)</option>`;
        });

        html += '</select>';
        container.innerHTML = html;
    }

    function createModal() {
        if (modalElement) {
            modalElement.remove();
        }

        injectStyles();

        modalElement = document.createElement('div');
        modalElement.className = 'title-import-overlay';
        modalElement.innerHTML = `
            <div class="title-import-window">
                <div class="title-import-header">
                    <h3 class="title-import-title">📋 Importar Títulos do NotebookLM</h3>
                    <button class="title-import-close" onclick="TitleImporter.close()">×</button>
                </div>
                <div class="title-import-body">
                    <div class="title-import-instructions">
                        <strong>Como usar:</strong> Cole os títulos da seção "Títulos usados como referência" 
                        do NotebookLM abaixo. Cada título será buscado automaticamente no banco de dados.
                    </div>
                    <textarea id="titleImportInput" class="title-import-textarea" 
                        placeholder="Cole os títulos aqui, um por linha...

Exemplo:
• Elucidações sobre o Mundo Espiritual e a Vida Cotidiana
• Perguntas e Respostas sobre a Fé e a Conduta Humana
• A Perspectiva Ampla e o Ponto Essencial"></textarea>
                    
                    <button class="title-import-btn title-import-btn-primary" onclick="TitleImporter.search()">
                        🔍 Buscar Títulos
                    </button>
                    
                    <div id="titleImportResults" class="title-import-results"></div>
                </div>
                <div class="title-import-actions" id="titleImportActions" style="display: none;">
                    <div id="pubSelectContainer"></div>
                    <button class="title-import-btn title-import-btn-primary" onclick="TitleImporter.addToPublication()">
                        ➕ Adicionar à Publicação
                    </button>
                </div>
            </div>
        `;

        modalElement.addEventListener('click', (e) => {
            if (e.target === modalElement) close();
        });

        document.addEventListener('keydown', handleKeyDown);
    }

    function handleKeyDown(e) {
        if (e.key === 'Escape' && modalElement && modalElement.parentNode) {
            close();
        }
    }

    async function open() {
        await loadSearchIndex();
        createModal();
        document.body.appendChild(modalElement);

        setTimeout(() => {
            const textarea = document.getElementById('titleImportInput');
            if (textarea) textarea.focus();
        }, 100);
    }

    function close() {
        if (modalElement && modalElement.parentNode) {
            modalElement.parentNode.removeChild(modalElement);
        }
        document.removeEventListener('keydown', handleKeyDown);
        foundArticles = [];
    }

    function search() {
        const textarea = document.getElementById('titleImportInput');
        if (!textarea || !textarea.value.trim()) {
            alert('Por favor, cole alguns títulos para buscar.');
            return;
        }

        const results = searchTitles(textarea.value);
        if (results.length === 0) {
            alert('Nenhum título encontrado. Verifique o formato.');
            return;
        }

        renderResults(results);
    }

    function addToPublication() {
        const select = document.getElementById('targetPubSelect');
        if (!select || !select.value) {
            alert('Por favor, selecione uma publicação.');
            return;
        }

        if (foundArticles.length === 0) {
            alert('Nenhum artigo para adicionar.');
            return;
        }

        let pubId = select.value;

        // Create new publication if needed
        if (pubId === '__NEW__') {
            const name = prompt('Nome da nova publicação:');
            if (!name || !name.trim()) return;

            const newPub = FavoritesManager.createPublication(name.trim());
            pubId = newPub.id;
        }

        // Add all found articles
        const addedCount = FavoritesManager.addMultipleToPublication(pubId, foundArticles);

        const pub = FavoritesManager.getPublication(pubId);
        alert(`${addedCount} artigo(s) adicionado(s) à publicação "${pub.name}"!`);

        // Refresh publication list in case a new one was created
        renderPublicationSelect();

        // Refresh the main page if available
        if (typeof loadPublicationList === 'function') {
            loadPublicationList();
        }

        close();
    }

    // Note: lastResults is declared at top of module

    function showPreview(index) {
        if (!lastResults[index] || !lastResults[index].found) return;

        const article = lastResults[index].article;

        // Remove existing preview if any
        const existing = document.querySelector('.title-import-article-preview');
        if (existing) existing.remove();

        const preview = document.createElement('div');
        preview.className = 'title-import-article-preview';
        preview.innerHTML = `
            <div class="title-import-preview-header">
                <div>
                    <h3 class="title-import-preview-title">${article.title}</h3>
                    <div class="title-import-preview-meta">${article.category || ''} ${article.year ? '• ' + article.year : ''}</div>
                </div>
                <button class="title-import-close" onclick="this.closest('.title-import-article-preview').remove()" style="background: #e2e8f0; color: #4a5568;">×</button>
            </div>
            <div class="title-import-preview-body">
                <p>${article.content_snippet || 'Sem conteúdo disponível.'}</p>
                ${article.url ? `<a href="${article.url}" target="_blank" class="title-import-preview-link">Abrir ensinamento completo →</a>` : ''}
            </div>
        `;

        document.body.appendChild(preview);

        // Close on click outside
        preview.addEventListener('click', (e) => {
            if (e.target === preview) preview.remove();
        });
    }

    // Wrap renderResults to store results
    const originalRenderResults = renderResults;
    function renderResultsWrapper(results) {
        lastResults = results;
        return originalRenderResults(results);
    }

    return {
        open,
        close,
        search,
        addToPublication,
        showPreview
    };
})();

window.TitleImporter = TitleImporter;
