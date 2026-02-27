"""
Seed script: inserts 125 richly-formatted test blogs (25 per service category)
into the MongoDB 'blogs' collection and refreshes the navbar.

Supported dynamicSection types used:
  h1, h2, h3, h4, h5, h6, text (with bold + hyperlinks), image, list

Usage:
    py seed_blogs.py
"""

import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

DB_NAME = "brands-out-loud"

CATEGORY_HEADINGS = {
    "business": "Latest Business Stories",
    "technology": "Tech Innovations",
    "gcc": "GCC Regional News",
    "sustainability": "Green Initiatives",
    "semiconductor": "Chip Industry Updates",
}

MAX_NAVBAR_POSTS = 3


BLOG_TOPICS = {
    "business": [
        ("The Future of Global Trade in 2025", "future-of-global-trade-2025"),
        ("How AI Is Transforming Corporate Decision Making", "ai-transforming-corporate-decision-making"),
        ("The Rise of Remote-First Enterprises", "rise-of-remote-first-enterprises"),
        ("Navigating Mergers and Acquisitions in Volatile Markets", "navigating-mergers-acquisitions-volatile-markets"),
        ("Leadership Strategies for Hyper-Growth Companies", "leadership-strategies-hyper-growth-companies"),
        ("The Power of Brand Storytelling in B2B Markets", "power-of-brand-storytelling-b2b-markets"),
        ("Supply Chain Resilience After Global Disruptions", "supply-chain-resilience-global-disruptions"),
        ("Startup Ecosystems: From Garage to Unicorn", "startup-ecosystems-garage-to-unicorn"),
        ("Corporate Governance Best Practices for 2025", "corporate-governance-best-practices-2025"),
        ("The Gig Economy: Redefining the Future of Work", "gig-economy-redefining-future-of-work"),
        ("Private Equity Trends Shaping Mid-Market Businesses", "private-equity-trends-mid-market-businesses"),
        ("Building a Culture of Innovation Within Large Organizations", "building-culture-innovation-large-organizations"),
        ("Customer-Centric Transformation: A Business Imperative", "customer-centric-transformation-business-imperative"),
        ("The Role of ESG in Modern Business Strategy", "role-of-esg-modern-business-strategy"),
        ("Subscription Models: The New Revenue Frontier", "subscription-models-new-revenue-frontier"),
        ("Family Business Succession Planning in the Digital Age", "family-business-succession-planning-digital-age"),
        ("Outsourcing Versus In-House: Making the Right Call", "outsourcing-vs-inhouse-making-right-call"),
        ("How Data Analytics Drives Smarter Business Strategies", "data-analytics-drives-smarter-business-strategies"),
        ("Franchising as a Growth Vehicle in Emerging Markets", "franchising-growth-vehicle-emerging-markets"),
        ("Navigating Regulatory Complexity Across Global Borders", "navigating-regulatory-complexity-global-borders"),
        ("The Psychology of Pricing and Its Impact on Sales", "psychology-of-pricing-impact-on-sales"),
        ("Cross-Border E-Commerce: Opportunities and Challenges", "cross-border-ecommerce-opportunities-challenges"),
        ("Building Strategic Partnerships That Last", "building-strategic-partnerships-that-last"),
        ("Workforce Upskilling: Why It Matters More Than Ever", "workforce-upskilling-why-it-matters-more-than-ever"),
        ("The New CFO: From Number-Cruncher to Strategic Advisor", "new-cfo-number-cruncher-to-strategic-advisor"),
    ],
    "technology": [
        ("Generative AI: Separating Hype From Reality", "generative-ai-separating-hype-from-reality"),
        ("The Edge Computing Revolution and What It Means for Business", "edge-computing-revolution-business-impact"),
        ("Quantum Computing: A Practical Overview for Enterprises", "quantum-computing-practical-overview-enterprises"),
        ("Cloud-Native Architecture: Building for Scale and Resilience", "cloud-native-architecture-scale-resilience"),
        ("Cybersecurity in the Age of AI-Powered Attacks", "cybersecurity-ai-powered-attacks-2025"),
        ("The API Economy: How Integrations Are Reshaping Software", "api-economy-integrations-reshaping-software"),
        ("DevOps to Platform Engineering: The Next Evolution", "devops-to-platform-engineering-evolution"),
        ("Ethical AI: Why Governance Frameworks Are Non-Negotiable", "ethical-ai-governance-frameworks-2025"),
        ("The Rise of Low-Code and No-Code Platforms", "rise-of-low-code-no-code-platforms"),
        ("Web3 Beyond the Hype: Practical Applications Today", "web3-beyond-hype-practical-applications"),
        ("5G Deployment: Real-World Impact Across Industries", "5g-deployment-real-world-impact-industries"),
        ("Digital Twins: Bridging the Physical and Digital Worlds", "digital-twins-bridging-physical-digital-worlds"),
        ("Open-Source Software: The Backbone of Modern Innovation", "open-source-software-backbone-modern-innovation"),
        ("Observability at Scale: Beyond Traditional Monitoring", "observability-at-scale-beyond-traditional-monitoring"),
        ("The Future of Human-Computer Interaction", "future-of-human-computer-interaction"),
        ("Data Mesh Architecture: A Decentralised Data Strategy", "data-mesh-architecture-decentralised-data-strategy"),
        ("AR and VR in the Enterprise: Practical Deployments", "ar-vr-enterprise-practical-deployments"),
        ("Supply Chain Technology: From Spreadsheets to AI", "supply-chain-technology-spreadsheets-to-ai"),
        ("Fintech Innovation: Disrupting Traditional Banking", "fintech-innovation-disrupting-traditional-banking"),
        ("Automation Paradox: More Robots, More Human Work", "automation-paradox-more-robots-more-human-work"),
        ("The Rise of Spatial Computing and What It Unlocks", "rise-of-spatial-computing-what-it-unlocks"),
        ("SaaS Consolidation: Why Enterprise Stacks Are Shrinking", "saas-consolidation-enterprise-stacks-shrinking"),
        ("Responsible Data Collection in a Post-Privacy World", "responsible-data-collection-post-privacy-world"),
        ("Microservices vs. Monoliths: The Ongoing Debate", "microservices-vs-monoliths-ongoing-debate"),
        ("Developer Experience: The Hidden Competitive Advantage", "developer-experience-hidden-competitive-advantage"),
    ],
    "gcc": [
        ("Gulf Cooperation Council's Vision for a Knowledge Economy", "gcc-vision-knowledge-economy-2025"),
        ("Saudi Arabia's NEOM: Building the City of the Future", "saudi-arabia-neom-city-of-the-future"),
        ("UAE's Diversification Strategy Beyond Oil", "uae-diversification-strategy-beyond-oil"),
        ("GCC Start-up Ecosystem: Where Are the Hottest Hubs?", "gcc-startup-ecosystem-hottest-hubs"),
        ("Tourism Boom in the Gulf: Opportunities and Infrastructure", "tourism-boom-gulf-opportunities-infrastructure"),
        ("GCC Sovereign Wealth Funds: Investing in the Global Future", "gcc-sovereign-wealth-funds-global-investments"),
        ("Logistics and Free Zones: The Gulf's Trade Advantage", "logistics-free-zones-gulf-trade-advantage"),
        ("Women in Leadership Across GCC Nations", "women-in-leadership-across-gcc-nations"),
        ("Renewable Energy Targets: Who Is Leading the Race?", "gcc-renewable-energy-targets-leaders"),
        ("Smart City Initiatives Transforming Gulf Capitals", "smart-city-initiatives-transforming-gulf-capitals"),
        ("Foreign Direct Investment Trends in the GCC Region", "fdi-trends-gcc-region-2025"),
        ("GCC Aviation Sector: Competing on the World Stage", "gcc-aviation-sector-global-competition"),
        ("Fintech Growth in the Middle East: Key Players", "fintech-growth-middle-east-key-players"),
        ("Healthcare Innovation in the Gulf: A Growing Priority", "healthcare-innovation-gulf-growing-priority"),
        ("Real Estate Market Dynamics Across GCC Cities", "real-estate-market-dynamics-gcc-cities"),
        ("Education Reform and Human Capital Development in the Gulf", "education-reform-human-capital-gcc"),
        ("Digital Government: E-Services Leading in the GCC", "digital-government-eservices-gcc"),
        ("GCC Defence Sector: Modernisation and Local Industry", "gcc-defence-sector-modernisation-local"),
        ("Halal Economy: An Untapped Global Market", "halal-economy-untapped-global-market"),
        ("Cultural Tourism and Heritage Conservation in the Gulf", "cultural-tourism-heritage-conservation-gulf"),
        ("Green Hydrogen: Can the GCC Lead the Global Supply Chain?", "green-hydrogen-gcc-global-supply-chain"),
        ("GCC Retail Transformation: Luxury, Value, and E-Commerce", "gcc-retail-transformation-luxury-ecommerce"),
        ("Blockchain Adoption in Gulf Financial Markets", "blockchain-adoption-gulf-financial-markets"),
        ("Youth Population Surge: Harnessing the Gulf's Demographic Dividend", "gulf-youth-demographic-dividend"),
        ("Manufacturing Ambitions: GCC's Push for Industrial Diversification", "manufacturing-ambitions-gcc-industrial-diversification"),
    ],
    "sustainability": [
        ("Net Zero 2050: Corporate Commitments Under the Microscope", "net-zero-2050-corporate-commitments"),
        ("Circular Economy Models Gaining Global Momentum", "circular-economy-models-global-momentum"),
        ("Carbon Credits: How the Market Really Works", "carbon-credits-how-market-really-works"),
        ("Green Buildings: Standards, Certifications, and ROI", "green-buildings-standards-certifications-roi"),
        ("Sustainable Fashion: Industry's Biggest Challenge", "sustainable-fashion-industrys-biggest-challenge"),
        ("The Business Case for Biodiversity Action", "business-case-for-biodiversity-action"),
        ("Clean Water Access: A Corporate Responsibility Imperative", "clean-water-access-corporate-responsibility"),
        ("Food Waste Technology: Innovations Cutting Losses", "food-waste-technology-innovations"),
        ("ESG Ratings: Do They Actually Measure Impact?", "esg-ratings-do-they-measure-impact"),
        ("Regenerative Agriculture: Healing Land While Feeding the World", "regenerative-agriculture-healing-land"),
        ("Plastic-Free Packaging: Where Industry Stands Today", "plastic-free-packaging-industry-today"),
        ("Electric Vehicle Supply Chain Sustainability Challenges", "ev-supply-chain-sustainability-challenges"),
        ("Blue Economy: Ocean-Based Sustainable Industries", "blue-economy-ocean-based-sustainable-industries"),
        ("Just Transition: Making Climate Action Socially Equitable", "just-transition-climate-action-social-equity"),
        ("Nature-Based Solutions as a Business Asset", "nature-based-solutions-business-asset"),
        ("Sustainable Finance: Green Bonds Market Outlook", "sustainable-finance-green-bonds-outlook"),
        ("Energy Efficiency: The Fastest Path to Carbon Reduction", "energy-efficiency-fastest-path-carbon-reduction"),
        ("Water Stewardship in Manufacturing: Real Best Practices", "water-stewardship-manufacturing-best-practices"),
        ("Scope 3 Emissions: The Hidden Climate Footprint", "scope-3-emissions-hidden-climate-footprint"),
        ("Impact Investing: Aligning Capital With Purpose", "impact-investing-aligning-capital-with-purpose"),
        ("Solar Energy Democratisation: From Rooftops to Utilities", "solar-energy-democratisation-rooftops-utilities"),
        ("Corporate Deforestation Commitments: Progress and Gaps", "corporate-deforestation-commitments-progress-gaps"),
        ("Life Cycle Assessment: A Tool for Greener Products", "life-cycle-assessment-greener-products"),
        ("The Role of Technology in Climate Adaptation", "technology-role-in-climate-adaptation"),
        ("Sustainable Supply Chain Transparency: Challenges and Solutions", "sustainable-supply-chain-transparency"),
    ],
    "semiconductor": [
        ("The Global Chip Shortage: Lessons Learned for 2025", "global-chip-shortage-lessons-learned-2025"),
        ("TSMC vs. Intel vs. Samsung: The Foundry Battle", "tsmc-intel-samsung-foundry-battle"),
        ("AI Chips: Designing for Inference at the Edge", "ai-chips-designing-for-inference-edge"),
        ("RISC-V: Open Architecture and Its Growing Ecosystem", "risc-v-open-architecture-growing-ecosystem"),
        ("Advanced Packaging: The New Frontier in Chip Performance", "advanced-packaging-new-frontier-chip-performance"),
        ("Semiconductor Geopolitics: Export Controls and Their Impact", "semiconductor-geopolitics-export-controls-impact"),
        ("Chiplet Architecture: Modular Design for the Next Decade", "chiplet-architecture-modular-design-next-decade"),
        ("Power Semiconductors: Driving the EV Revolution", "power-semiconductors-driving-ev-revolution"),
        ("Photonics Integration: Light-Based Computing Is Here", "photonics-integration-light-based-computing"),
        ("Memory Technology Evolution: From DRAM to HBM", "memory-technology-evolution-dram-to-hbm"),
        ("The Economics of a Semiconductor Fab: Eye-Watering Costs", "economics-semiconductor-fab-costs"),
        ("Design Automation Tools Transforming the Chip Industry", "design-automation-tools-chip-industry"),
        ("GaN and SiC: Wide-Bandgap Semiconductors in Focus", "gan-sic-wide-bandgap-semiconductors"),
        ("India's Semiconductor Ambitions: Plan Meets Reality", "india-semiconductor-ambitions-plan-meets-reality"),
        ("Quantum Dot Displays: From Lab to Living Room", "quantum-dot-displays-lab-to-living-room"),
        ("Edge AI Inference: Chips That Think Without the Cloud", "edge-ai-inference-chips-without-cloud"),
        ("MEMS Sensors: The Invisible Technology in Your Devices", "mems-sensors-invisible-technology-devices"),
        ("IoT Chip Requirements: Balancing Performance and Power", "iot-chip-requirements-performance-power"),
        ("Analogue Design Renaissance in a Digital World", "analogue-design-renaissance-digital-world"),
        ("Environmental Impact of Semiconductor Manufacturing", "environmental-impact-semiconductor-manufacturing"),
        ("Automotive Semiconductors: Safety-Critical Design Challenges", "automotive-semiconductors-safety-critical-design"),
        ("Neuromorphic Computing: Chips That Mimic the Brain", "neuromorphic-computing-chips-mimic-brain"),
        ("The Workforce Crisis in Semiconductor Engineering", "workforce-crisis-semiconductor-engineering"),
        ("3D NAND Flash: Stacking the Future of Storage", "3d-nand-flash-stacking-future-storage"),
        ("Heterogeneous Integration: Mixing Technologies for Performance", "heterogeneous-integration-mixing-technologies"),
    ],
}


def build_dynamic_sections(slug: str, title: str, category: str) -> list:
    """Build a rich set of dynamic sections that exercises every supported type."""
    img_seed_1 = f"{slug}-inline-1"
    img_seed_2 = f"{slug}-inline-2"

    return [
        {
            "type": "h1",
            "id": f"{slug}-overview",
            "content": f"Overview: {title}",
        },
        {
            "type": "text",
            "content": (
                f"The {category} landscape is undergoing a profound shift in 2025. "
                f"<strong>Organisations that understand these macro-level forces early gain a decisive competitive edge.</strong> "
                f"This article explores the critical dynamics at play, drawing on research from leading analysts and first-hand "
                f"accounts from industry practitioners. Whether you are a <strong>C-suite leader</strong>, a mid-level "
                f"manager, or an entrepreneur just starting out, the insights below will help you navigate what lies ahead. "
                f"For a broader market perspective, we recommend the "
                f'<a href="/" style="color:#3533CD;text-decoration:underline;">Brands Out Loud homepage</a>, '
                f"where our editorial team curates the very best stories every week."
            ),
        },
        {
            "type": "h2",
            "id": f"{slug}-key-drivers",
            "content": "Key Drivers Reshaping the Industry",
        },
        {
            "type": "text",
            "content": (
                "Three interconnected forces are reshaping how companies in this space operate. "
                "<strong>First, digitalisation</strong> is compressing timelines and eliminating middlemen. "
                "<strong>Second, regulatory pressure</strong> — particularly around data privacy and environmental disclosure — "
                "is raising the compliance bar for every organisation. "
                "<strong>Third, talent scarcity</strong> is forcing leaders to rethink hiring, retention, and workforce development. "
                "Together, these forces create both extraordinary risk and extraordinary opportunity."
            ),
        },
        {
            "type": "list",
            "items": [
                "Accelerated digitalisation compressing traditional timelines",
                "Rising regulatory scrutiny across data, environment, and labour",
                "Intense competition for skilled talent in niche domains",
                "Shifting consumer expectations demanding transparency and speed",
                "Geopolitical realignments disrupting established supply chains",
                "Emergence of new business models enabled by AI and automation",
            ],
        },
        {
            "type": "h1",
            "id": f"{slug}-strategic-playbook",
            "content": "The Strategic Playbook for Leaders",
        },
        {
            "type": "text",
            "content": (
                "Leading organisations are not waiting for the dust to settle — "
                "they are making bold moves right now. "
                '<a href="/business" style="color:#3533CD;text-decoration:underline;">Business leaders</a> '
                "are restructuring their operating models to be more agile and data-driven. "
                "The most effective approach combines <strong>short-term operational tightening</strong> with "
                "<strong>long-term capability building</strong>. Companies that invest only in one side of this equation "
                "invariably fall behind."
            ),
        },
        {
            "type": "image",
            "content": {
                "url": f"https://picsum.photos/seed/{img_seed_1}/1200/500",
                "alt": f"Strategic framework illustration for {title}",
            },
        },
        {
            "type": "h2",
            "id": f"{slug}-operational-excellence",
            "content": "Operational Excellence: Doing More With Less",
        },
        {
            "type": "text",
            "content": (
                "Operational excellence is no longer a buzzword — it is a survival requirement. "
                "<strong>Lean principles, originally pioneered in manufacturing, are now standard practice</strong> "
                "in software development, financial services, and even creative industries. "
                "The key is ruthless prioritisation: identifying the 20% of activities that generate 80% of the value, "
                "and eliminating or automating the rest. "
                "This is easier said than done, but organisations that master it consistently outperform peers on margin "
                "and customer satisfaction metrics."
            ),
        },
        {
            "type": "h3",
            "content": "Process Automation: Where to Start",
        },
        {
            "type": "text",
            "content": (
                "For most organisations, the lowest-hanging fruit lies in repetitive, rules-based back-office tasks. "
                "<strong>Accounts payable, employee onboarding, and report generation</strong> are prime automation candidates — "
                "typically delivering 60–80% time savings with payback periods under 12 months. "
                "More complex cognitive tasks, such as contract review and strategic planning, require more sophisticated "
                "AI tools and a longer implementation runway."
            ),
        },
        {
            "type": "h4",
            "content": "Selecting the Right Automation Tools",
        },
        {
            "type": "list",
            "items": [
                "Map existing workflows before buying any software",
                "Pilot on a single process and measure ROI rigorously",
                "Prioritise platforms with strong API ecosystems for future integration",
                "Build a change management plan alongside the technical deployment",
                "Establish clear ownership and governance for each automated workflow",
            ],
        },
        {
            "type": "h1",
            "id": f"{slug}-innovation-culture",
            "content": "Building an Innovation Culture That Sticks",
        },
        {
            "type": "text",
            "content": (
                "Culture is the invisible architecture that determines whether innovation thrives or withers. "
                "<strong>Psychological safety — the belief that one can speak up without fear of punishment — "
                "is the single most important predictor of team innovation</strong>, according to Google's landmark Project Aristotle research. "
                "Leaders who model vulnerability, celebrate intelligent failures, and reward experimentation create "
                "environments where breakthrough ideas are far more likely to emerge. "
                "This is not soft management; it is a hard competitive advantage."
            ),
        },
        {
            "type": "h2",
            "id": f"{slug}-measuring-innovation",
            "content": "Measuring Innovation Without Killing It",
        },
        {
            "type": "text",
            "content": (
                "The instinct to measure everything can paradoxically stifle the very creativity you are trying to nurture. "
                "The best organisations use a <strong>dual-track measurement approach</strong>: "
                "rigorously tracking the output of mature innovation programmes while giving early-stage ideas breathing room. "
                '<a href="/technology" style="color:#3533CD;text-decoration:underline;">Technology-driven teams</a> '
                "often use Objectives and Key Results (OKRs) at the portfolio level rather than the project level, "
                "giving individual teams the freedom to pivot without losing sight of broader goals."
            ),
        },
        {
            "type": "image",
            "content": {
                "url": f"https://picsum.photos/seed/{img_seed_2}/1200/500",
                "alt": f"Innovation and collaboration visual for {title}",
            },
        },
        {
            "type": "h5",
            "content": "Quick Wins to Kickstart Your Innovation Journey",
        },
        {
            "type": "list",
            "items": [
                "Host a quarterly internal hackathon open to all departments",
                "Create a shared idea repository visible company-wide",
                "Dedicate 10% of engineering or R&D time to exploratory projects",
                "Recognise and reward teams that run smart experiments, even failed ones",
                "Form cross-functional squads to break down silo mentalities",
            ],
        },
        {
            "type": "h1",
            "id": f"{slug}-looking-ahead",
            "content": "Looking Ahead: What the Next 12 Months Hold",
        },
        {
            "type": "text",
            "content": (
                "The next 12 months will be defined by the choices organisations make today. "
                "<strong>Those who invest in capability, culture, and data infrastructure now</strong> will be "
                "significantly better positioned when market conditions stabilise. "
                "Conversely, those who hunker down and wait will find that the gap between them and more proactive "
                "competitors has grown too wide to close quickly. "
                "The time to act is not when the future becomes certain — because it never does — "
                "but when the <strong>cost of inaction clearly exceeds the cost of bold, measured action</strong>."
            ),
        },
        {
            "type": "h6",
            "content": "Editor's Note",
        },
        {
            "type": "text",
            "content": (
                "This article is part of Brands Out Loud's ongoing series on industry transformation and leadership excellence. "
                "We publish in-depth analysis every week across business, technology, GCC, sustainability, and semiconductor sectors. "
                '<a href="/" style="color:#3533CD;text-decoration:underline;">Return to the homepage</a> '
                "to explore our latest coverage."
            ),
        },
    ]


def build_blog_document(title: str, slug: str, category: str, index: int) -> dict:
    """Construct a complete blog document ready for MongoDB insertion."""
    base_date = "2025-01-15"
    days_offset = index * 3
    from datetime import date, timedelta
    blog_date = date(2025, 1, 15) + timedelta(days=days_offset)
    date_str = blog_date.strftime("%Y-%m-%d")

    return {
        "slug": slug,
        "status": "published",
        "isDeleted": False,
        "date": date_str,
        "created_at": time.time() - (days_offset * 86400),
        "blogContent": {
            "blogTitle": title,
            "blogSummary": (
                f"A comprehensive deep-dive into {title.lower()}, examining the forces driving change, "
                f"strategic frameworks for leaders, and the key decisions that will define success in the "
                f"{category.upper()} sector over the next 12 months."
            ),
            "blogCategory": category,
            "mainImageUrl": f"https://picsum.photos/seed/{slug}/1200/600",
            "mainImageAlt": f"Featured image for {title}",
            "dynamicSections": build_dynamic_sections(slug, title, category),
        },
    }


async def update_navbar_collection(db) -> None:
    """Rebuild the navbar collection from the latest published blogs per category."""
    navbar_data = {}

    for category_key, heading in CATEGORY_HEADINGS.items():
        category_filter = {
            "status": "published",
            "blogContent.blogCategory": {"$regex": f"^{category_key}$", "$options": "i"},
        }
        cursor = db["blogs"].find(category_filter).sort("created_at", -1).limit(MAX_NAVBAR_POSTS)
        blogs = await cursor.to_list(length=MAX_NAVBAR_POSTS)

        posts = []
        for blog in blogs:
            blog_content = blog.get("blogContent", {})
            posts.append({
                "title": blog_content.get("blogTitle", "Untitled"),
                "image_url": blog_content.get("mainImageUrl", ""),
                "slug": blog.get("slug", ""),
            })

        navbar_data[category_key] = {"heading": heading, "posts": posts}

    existing = await db["navbar"].find_one({})
    if existing:
        await db["navbar"].update_one({"_id": existing["_id"]}, {"$set": navbar_data})
    else:
        await db["navbar"].insert_one(navbar_data)


async def seed() -> None:
    mongo_url = os.getenv("mongo_public_url")
    if not mongo_url:
        raise ValueError("mongo_public_url is not set in .env")

    client = AsyncIOMotorClient(mongo_url)
    db = client[DB_NAME]

    print(f"Connected to MongoDB — database: '{DB_NAME}'\n")

    total_inserted = 0
    total_skipped = 0

    for category, topics in BLOG_TOPICS.items():
        print(f"  Category: {category.upper()}")
        for index, (title, slug) in enumerate(topics):
            existing = await db["blogs"].find_one({"slug": slug})
            if existing:
                print(f"    [SKIP] {slug}")
                total_skipped += 1
                continue

            doc = build_blog_document(title, slug, category, index)
            await db["blogs"].insert_one(doc)
            print(f"    [OK]   {slug}")
            total_inserted += 1

    print(f"\nInserted: {total_inserted}  |  Skipped (already exists): {total_skipped}")

    print("\nUpdating navbar collection...")
    await update_navbar_collection(db)
    print("Navbar updated.\n")

    print("Done. All blogs have been seeded.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
