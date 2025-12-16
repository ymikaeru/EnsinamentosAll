/**
 * Showa Year Converter
 * Converts Japanese Showa era years to Western calendar years
 * Showa 1 (昭和1年) = 1926, so Showa N = 1925 + N
 */
(function () {
    'use strict';

    // Map fullwidth digits to halfwidth
    const fullwidthToHalfwidth = {
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
    };

    function convertFullwidthToNumber(str) {
        let result = '';
        for (let char of str) {
            result += fullwidthToHalfwidth[char] || char;
        }
        return parseInt(result, 10);
    }

    function convertShowaToWestern(showaYear) {
        return 1925 + showaYear;
    }

    function processHeaders() {
        // Find all elements that match period headers
        const selectors = [
            'p > font[size="4"] > strong',
            'p > font[size="4"]',
            'font[size="4"] > strong'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                const text = el.textContent || el.innerText;

                // Match patterns like 昭和２４年 or 昭和24年
                const showaPattern = /昭和([０-９\d]+)年/;
                const match = text.match(showaPattern);

                if (match && !el.dataset.converted) {
                    const showaYear = convertFullwidthToNumber(match[1]);
                    const westernYear = convertShowaToWestern(showaYear);

                    // Add Western year in parentheses
                    const newText = text.replace(
                        showaPattern,
                        `昭和${match[1]}年 (${westernYear})`
                    );

                    el.textContent = newText;
                    el.dataset.converted = 'true';
                }
            });
        });
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', processHeaders);
    } else {
        processHeaders();
    }
})();
