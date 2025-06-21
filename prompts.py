"""
Prompts for AI generation features
"""

def get_business_canvas_prompt(context):
    return f"""
Act as an expert business strategist and senior frontend developer. Your task is to create a complete, visually clean, and well-structured HTML Business Model Canvas based on the provided context. The final output must be a single, self-contained HTML file.

**CONTEXT FROM UPLOADED FILES:**
{context if context else "No context files were provided."}

**--- CORE TASK & INSTRUCTIONS ---**

**1. Analyze and Populate:**
- Carefully analyze the business information provided in the "CONTEXT" section.
- Populate all nine sections of the Business Model Canvas with relevant, concise bullet points derived from the context. The content should be strategic and to the point.

**2. Fallback Scenario:**
- If no context is provided, invent a compelling and detailed fictional tech startup. Do not use a generic example. Be specific, e.g., "AstraFlow," a platform that uses AI to automate and optimize supply chain logistics for e-commerce businesses. Then, fill out the canvas for this fictional company.

**--- DESIGN & TECHNICAL REQUIREMENTS ---**

**1. Frameworks and Libraries (MUST USE):**
- **Tailwind CSS:** For all styling, loaded from the CDN.
- **Google Fonts:** For the 'Inter' font family.
- **Google Material Symbols (Outlined):** For all icons, loaded from the Google Fonts CDN.

**2. Layout (CRITICAL):**
- You MUST use the exact HTML structure and CSS Grid layout provided in the template below.
- The canvas must be responsive, collapsing gracefully into a single column on smaller screens (e.g., mobile). Use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`).

**3. Styling:**
- Adhere to a clean, professional, and minimalist design inspired by the Strategyzer canvas.
- Each canvas section (grid-item) should be a card with a light background (`bg-gray-50` or `bg-white`), rounded corners (`rounded-lg`), and a subtle box shadow (`shadow-md`).
- Use a professional color for the icon and title in each section (e.g., `text-gray-700`).
- Ensure excellent padding and spacing throughout for readability.

**4. Iconography:**
- You MUST use the specific Google Material Symbols defined within the HTML template. Implement them using `<span class="material-symbols-outlined">icon_name</span>`.

**5. Warning:**
- ONLY OUTPUT THE HTML CODE, NO OTHER TEXT OR MARKDOWN.

**--- HTML TEMPLATE (USE THIS EXACT STRUCTURE) ---**

You must use this template as the foundation for your response. Populate the `<ul>` elements with the business content.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Model Canvas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; font-size: 28px; }}
        /* Responsive grid layout */
        .canvas-grid {{
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: 1rem;
        }}
        @media (min-width: 1024px) {{
            .canvas-grid {{
                grid-template-columns: repeat(5, 1fr);
                grid-template-rows: auto auto auto;
            }}
            .grid-item-kp {{ grid-column: 1 / 2; grid-row: 1 / 3; }}
            .grid-item-ka {{ grid-column: 2 / 3; grid-row: 1 / 2; }}
            .grid-item-vp {{ grid-column: 3 / 4; grid-row: 1 / 3; }}
            .grid-item-cr {{ grid-column: 4 / 5; grid-row: 1 / 2; }}
            .grid-item-cs {{ grid-column: 5 / 6; grid-row: 1 / 3; }}
            .grid-item-kr {{ grid-column: 2 / 3; grid-row: 2 / 3; }}
            .grid-item-ch {{ grid-column: 4 / 5; grid-row: 2 / 3; }}
            .grid-item-cst {{ grid-column: 1 / 4; grid-row: 3 / 4; }}
            .grid-item-rs {{ grid-column: 4 / 6; grid-row: 3 / 4; }}
        }}
    </style>
</head>
<body class="bg-gray-100 p-4 sm:p-6 lg:p-8">

    <div class="max-w-7xl mx-auto">
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-800">Business Model Canvas</h1>
            <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600 mt-2">
                <p><span class="font-semibold">Designed for:</span> [Company Name]</p>
                <p><span class="font-semibold">Date:</span> [Current Date]</p>
                <p><span class="font-semibold">Version:</span> 1.0</p>
            </div>
        </header>

        <main class="canvas-grid">
            <section class="grid-item-kp bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-blue-600">handshake</span>
                    <h2 class="text-lg font-semibold text-gray-800">Key Partners</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-ka bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-green-600">checklist</span>
                    <h2 class="text-lg font-semibold text-gray-800">Key Activities</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-vp bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-purple-600">redeem</span>
                    <h2 class="text-lg font-semibold text-gray-800">Value Propositions</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-cr bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-red-600">favorite</span>
                    <h2 class="text-lg font-semibold text-gray-800">Customer Relationships</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>
            
            <section class="grid-item-cs bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-orange-600">groups</span>
                    <h2 class="text-lg font-semibold text-gray-800">Customer Segments</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-kr bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-green-600">build_circle</span>
                    <h2 class="text-lg font-semibold text-gray-800">Key Resources</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-ch bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-red-600">local_shipping</span>
                    <h2 class="text-lg font-semibold text-gray-800">Channels</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>

            <section class="grid-item-cst bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-cyan-600">payments</span>
                    <h2 class="text-lg font-semibold text-gray-800">Cost Structure</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>
            
            <section class="grid-item-rs bg-white p-4 rounded-lg shadow-md flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="material-symbols-outlined text-teal-600">attach_money</span>
                    <h2 class="text-lg font-semibold text-gray-800">Revenue Streams</h2>
                </div>
                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                    </ul>
            </section>
        </main>
    </div>
</body>
</html>
```
"""


def get_value_proposition_prompt(context):
    return f"""
Act as an expert product manager and senior frontend developer. Your specialty is translating complex business frameworks into clear, intuitive, and visually appealing web interfaces. Your task is to create a complete HTML Value Proposition Canvas based on the provided context.

**CONTEXT FROM UPLOADED FILES:**
{context if context else "No context files were provided."}

**--- CORE TASK & INSTRUCTIONS ---**

**1. Analyze and Populate:**
- Carefully analyze the business information in the "CONTEXT" section to understand the customer and the product.
- Populate all six sub-sections of the Value Proposition Canvas (Gains, Pains, Customer Jobs, Gain Creators, Pain Relievers, Products & Services) with relevant, concise bullet points derived from the context.

**2. Fallback Scenario:**
- If no context is provided, invent a compelling and detailed fictional company. Be specific, for example: "MindEase," a mobile app that provides AI-driven cognitive behavioral therapy (CBT) exercises and guided meditations for anxiety relief. Fill out the canvas for this fictional company.

**--- DESIGN & TECHNICAL REQUIREMENTS ---**

**1. Frameworks and Libraries (MUST USE):**
- **Tailwind CSS:** For all styling, loaded from the CDN.
- **Google Fonts:** For the 'Inter' font family.
- **Google Material Symbols (Outlined):** For all icons, loaded from the Google Fonts CDN.

**2. Layout (CRITICAL):**
- You MUST use the exact HTML structure provided in the template below.
- The layout should be a two-column design on larger screens, representing the "Value Proposition" square and the "Customer Profile" circle, with a connecting arrow between them.
- The canvas must be responsive, stacking the two columns vertically on smaller screens.

**3. Styling:**
- The "Value Proposition" side should use a blue color scheme for its icons and titles.
- The "Customer Profile" side should use a red/pink color scheme.
- Each sub-section should be a clearly defined card or area with ample padding.
- Maintain a clean, professional, and minimalist aesthetic.

**4. Iconography:**
- You MUST use the specific Google Material Symbols defined within the HTML template.

**5. Warning:**
- ONLY OUTPUT THE HTML CODE, NO OTHER TEXT OR MARKDOWN.

**--- HTML TEMPLATE (USE THIS EXACT STRUCTURE) ---**

You must use this template as the foundation for your response. Populate the `<ul>` elements with the business content.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Value Proposition Canvas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; font-size: 28px; }}
        .vp-icon {{ font-size: 48px; }} /* Larger icons for central elements */
    </style>
</head>
<body class="bg-gray-100 p-4 sm:p-6 lg:p-8">

    <div class="max-w-7xl mx-auto">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-gray-800">Value Proposition Canvas</h1>
            <p class="text-gray-600 mt-1">For [Company Name / Product Name]</p>
        </header>

        <main class="grid grid-cols-1 lg:grid-cols-2 lg:items-center gap-8">

            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold text-center text-blue-600 mb-6">Value Proposition</h2>
                <div class="grid grid-cols-2 grid-rows-2 gap-4 min-h-[350px]">
                    <div class="row-span-2 flex flex-col items-center justify-center bg-blue-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined vp-icon text-blue-600">inventory_2</span>
                        <h3 class="text-lg font-semibold text-blue-800 mt-2">Products & Services</h3>
                        <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-2 text-center">
                            </ul>
                    </div>
                    <div class="flex flex-col items-center justify-center bg-blue-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined vp-icon text-blue-600">auto_awesome</span>
                        <h3 class="text-lg font-semibold text-blue-800 mt-2">Gain Creators</h3>
                        <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-2">
                            </ul>
                    </div>
                    <div class="flex flex-col items-center justify-center bg-blue-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined vp-icon text-blue-600">pill</span>
                        <h3 class="text-lg font-semibold text-blue-800 mt-2">Pain Relievers</h3>
                        <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-2">
                            </ul>
                    </div>
                </div>
            </div>

            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold text-center text-red-600 mb-6">Customer Profile</h2>
                <div class="flex flex-col gap-4 min-h-[350px]">
                     <div class="flex-1 flex items-center gap-4 bg-red-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined text-red-600 text-4xl">sentiment_very_satisfied</span>
                        <div>
                            <h3 class="text-lg font-semibold text-red-800">Gains</h3>
                            <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-1">
                                </ul>
                        </div>
                    </div>
                     <div class="flex-1 flex items-center gap-4 bg-red-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined text-red-600 text-4xl">sentiment_very_dissatisfied</span>
                        <div>
                            <h3 class="text-lg font-semibold text-red-800">Pains</h3>
                            <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-1">
                                </ul>
                        </div>
                    </div>
                     <div class="flex-1 flex items-center gap-4 bg-red-50 p-4 rounded-lg">
                        <span class="material-symbols-outlined text-red-600 text-4xl">fact_check</span>
                        <div>
                            <h3 class="text-lg font-semibold text-red-800">Customer Jobs</h3>
                            <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 mt-1">
                                </ul>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
```

Return ONLY the complete HTML code, no markdown formatting.
"""