const GeminiService = {
    // Configuration
    DEFAULT_MODEL: 'gemini-1.5-flash',
    API_URL: 'https://generativelanguage.googleapis.com/v1beta/models',

    // Key & Model Management
    getKey: () => localStorage.getItem('GEMINI_API_KEY'),
    setKey: (key) => {
        if (!key) {
            localStorage.removeItem('GEMINI_API_KEY');
            return;
        }
        localStorage.setItem('GEMINI_API_KEY', key.trim());
    },
    hasKey: () => !!localStorage.getItem('GEMINI_API_KEY'),

    getModel: () => localStorage.getItem('GEMINI_MODEL') || 'gemini-1.5-flash',
    setModel: (model) => {
        if (model) localStorage.setItem('GEMINI_MODEL', model);
    },

    // Core Generation Function
    async generateContent(prompt) {
        const key = this.getKey();
        if (!key) throw new Error("API Key not configured");

        const model = this.getModel();
        const response = await fetch(`${this.API_URL}/${model}:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error?.message || "Gemini API Error");
        }

        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    },

    // Specific Features

    /**
     * Optimizes a natural language query into search keywords.
     * Focuses on extracting rare, discriminative concepts rather than generic synonyms.
     */
    /**
     * Optimizes a natural language query into search keywords.
     * Returns a structured object: { mandatory: [], optional: [] }
     */
    async optimizeSearchQuery(userQuery) {
        const prompt = `
            Act as a search optimizer for a religious teaching database (Messianic Church).
            User Query: "${userQuery}"
            
            Task: Analyze the query and extract keywords into two categories:
            1. MANDATORY: The core subject. If a document doesn't have this, it is IRRELEVANT. (e.g., "quadris", "johrei", "meishusama").
            2. OPTIONAL: Context words, synonyms, or related concepts that improve ranking but are not required. (e.g., "dor", "cura", "ensinamento").

            - IGNORE generics: "sobre", "como", "gostaria", "saber", "fazer", "ter", "para", "preparação", "descendência" (unless explicit context).
            
            OUTPUT JSON ONLY:
            {
                "mandatory": ["word1", "word2"],
                "optional": ["word3", "word4"]
            }
            
            Examples:
            "Como ter harmonia no lar?" -> {"mandatory": ["harmonia"], "optional": ["lar", "família", "paz", "conflito"]}
            "Dor no ombro" -> {"mandatory": ["ombro"], "optional": ["dor", "purificação", "braço"]}
            "Pontos focais para o quadris" -> {"mandatory": ["quadris"], "optional": ["cintura", "nervo", "ciático", "perna"]}
        `;

        try {
            const raw = await this.generateContent(prompt);

            // Clean markdown
            const jsonMatch = raw.match(/\{[\s\S]*\}/);
            const jsonStr = jsonMatch ? jsonMatch[0] : raw.replace(/```json|```/g, '').trim();

            return JSON.parse(jsonStr);
        } catch (e) {
            console.error("Gemini optimization failed:", e);
            // Fallback: treat whole query as mandatory? Or just return null
            return { mandatory: userQuery.trim().split(/\s+/), optional: [] };
        }
    },

    /**
     * Reranks a list of candidate items based on the query.
     * Uses semantic understanding to order the best matches first.
     */
    async rerankItems(userQuery, items) {
        if (items.length === 0) return [];

        // We can only send a limited context. Top 20 items max.
        const candidates = items.slice(0, 20);

        const prompt = `
            I have a user query and a list of candidate articles.
            Query: "${userQuery}"
            
            Candidates:
            ${candidates.map((item, index) => `[ID:${index}] ${item.title} (Snippet: ${(item.content_snippet || '').substring(0, 100)}...)`).join('\n')}
            
            Task: Return a valid JSON array of indices for the 5 MOST RELEVANT articles.
            - Prioritize direct answers to the question.
            - RETURN ONLY THE JSON ARRAY. NO TEXT.
            - Example: [3, 0, 1]
        `;

        try {
            const raw = await this.generateContent(prompt);
            // Extract JSON from potential markdown blocks or surrounding text
            // Matches anything looking like [ ... ] or [ ...
            const jsonMatch = raw.match(/\[[\s\S]*\]/);
            const jsonStr = jsonMatch ? jsonMatch[0] : raw.replace(/```json|```/g, '').trim();

            const indices = JSON.parse(jsonStr);

            if (Array.isArray(indices)) {
                return indices.map(i => candidates[i]).filter(Boolean);
            }
            return candidates; // Fallback
        } catch (e) {
            console.error("Gemini rerank failed:", e);
            return candidates; // Fallback
        }
    }
};

window.GeminiService = GeminiService;
