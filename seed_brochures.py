import os
import django
from django.core.files import File

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from blog.models import Brochure

assets_dir = r"d:\Iraya\platform-iraya-website\assets\brochures"

brochures_data = [
    {
        "title": "ElasticDocs",
        "image_file": "ED-Cover.webp",
        "image_max_width": "400px",
        "image_max_height": "380px",
        "card_height": 350,
        "text_content": "Wouldn't it be practical if your geoscientists, engineers, and data managers can discover and analyse earth\n                  data speedily instead of spending more than 50% of their time searching or reacquiring expensive energy data?<br>\n                  <br>The best solution to this data problem is ElasticDocs™, our Intuitive Knowledge Container. It can quickly and\n                  easily transform unstructured data to reader-friendly structured data.",
        "text_column_classes": "pl-xl-2 pl-md-16 mt-6",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Data Atelier",
        "image_file": "DA-Cover.webp",
        "image_max_width": "420px",
        "image_max_height": "320px",
        "card_height": 350,
        "text_content": "The Data Atelier is a digital factory that is composed of an orchestration of pipelines, data tracking, \n                  and monitoring services. It provides an intelligent engine that runs the internal processes and machine learning\n                  algorithms that come with production.<br>\n                  <br>When optimized, it drives the cost of production down by ensuring economy-of-scale. In addition, it is fully customizable \n                  based on your company's data management needs.",
        "text_column_classes": "pl-xl-2 pl-md-16 mt-8",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Bonaparte 400",
        "image_file": "Bonaparte-400.webp",
        "image_max_width": "400px",
        "image_max_height": "360px",
        "card_height": 420,
        "text_content": "Turning data into knowledge, we at Iraya Energies have processed over 70 years' worth of data on the Bonaparte \n                  Basin using leading edge Machine Learning (ML) and Artificial Intelligence (AI). This includes nearly 254,000 \n                  images of tables, maps, seismic and stratigraphic charts, thin sections, cores which are unstructured data that\n                  comes in pdf, document, and PowerPoint formats.<br>\n                  <br>Using ElasticDocs, our intuitive knowledge container, they are absorbed and tagged automatically, resulting in\n                  Bonaparte 400, a cache of valuable information that is instantly retrievable and analytic-ready.",
        "text_column_classes": "pl-xl-2 pl-md-16 mt-12",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "EarthDoc",
        "image_file": "ED2K-Cover.webp",
        "image_max_width": "350px",
        "image_max_height": "360px",
        "card_height": 480,
        "text_content": "For over 70 years, The European Association of Geoscientists and Engineers (EAGE) has been responsible for publishing\n                 and gathering data on conferences and publications in the field of geoscience. The EarthDoc online database contains more\n                 than 70,000 scientific publications and technical papers as well as conference proceedings. <br>\n                 Using ElasticDocs, our intuitive knowledge container, they are absorbed and tagged automatically, resulting in\n                 Bonaparte 400, a cache of valuable information that is instantly retrievable and analytic-ready.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-16",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Asset Management",
        "image_file": "ED-DA-for-Asset-Management.webp",
        "image_max_width": "440px",
        "image_max_height": "380px",
        "card_height": 350,
        "text_content": "In general, unstructured data is poorly utilized: 90% of data is unstructured and only \n                  5 - 10% of these are being optimized through reuse. <br>\n                 <br>In addition, the unavailability of unstructured data leads to an increase of 13% in \n                 non-productive time, since extra man hours are required to be allotted to data retrieval. \n                 Non-accessible data negatively disrupt businesses. The success of asset management starts \n                 with well-organized data.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-2",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "ESG",
        "image_file": "ED-DA-for-ESG_small.webp",
        "image_max_width": "520px",
        "image_max_height": "380px",
        "card_height": 450,
        "text_content": "In Environmental, Social and Corporate Governance (ESG), risks and opportunities related to \n                  sustainability are recognized, evaluated, and managed under a holistic framework with respect \n                  to stakeholders relating to environmental, social and governance aspects. <br>\n                 <br>Despite the differing practices and standards in each of these domains, they show how \n                 determined an organization is to create elevated enterprise value.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-2",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Mining",
        "image_file": "ED-DA-for-Mining.webp",
        "image_max_width": "550px",
        "image_max_height": "380px",
        "card_height": 480,
        "text_content": "Iraya's Data Atelier and ElasticDocs have all the digital capabilities to support the mining\n                  operations of an organization's biggest asset class - unstructured data.<br>\n                 \n                 <br>The Data Atelier is an AI-enabled digital factory solution that can be connected to \n                 internal front-end applications, or Iraya's proprietary knowledge container, ElasticDocs. \n                 It leapfrogs the access of unstructured data for smart and sustainable data mining operations. \n                 Through its innovative search-and-cluster technology, ElasticDocs enables professionals to browse\n                through thousands of files in seconds. Interrogate all your files in a single query.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-2",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "DataShopper",
        "image_file": "DS-Cover.webp",
        "image_max_width": "550px",
        "image_max_height": "380px",
        "card_height": 400,
        "text_content": "DataShopper is an extension to both ElasticDocs and Data Atelier to ease data digitalization \n                  and data wrangling activities.<br>\n                 \n                  <br>It can be used to enhance geoscience parameter extraction. Digital twin developments, project \n                  management, and engineering & asset management. Thousands or even up to a million-rows of data \n                  digitalization is typically required for internal database population, data processing and analysis. \n                  DataShopper can help improve digitization accuracy with human-in-the-loop & AI-powered user interface.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-2",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Enhanced Geothermal System",
        "image_file": "DA-for-Enhanced-Geothermal-System.webp",
        "image_max_width": "510px",
        "image_max_height": "380px",
        "card_height": 480,
        "text_content": "Iraya's Data Atelier and ElasticDocs have all the digital capabilities to support the mining\n                  operations of an organization's biggest asset class - unstructured data.<br>\n                 \n                 <br>The Data Atelier is an AI-enabled digital factory solution that can be connected to \n                 internal front-end applications, or Iraya's proprietary knowledge container, ElasticDocs. \n                 It leapfrogs the access of unstructured data for smart and sustainable data mining operations. \n                 Through its innovative search-and-cluster technology, ElasticDocs enables professionals to browse\n                through thousands of files in seconds. Interrogate all your files in a single query.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-2",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Metal Mining",
        "image_file": "DA-for-Metal-Mining.webp",
        "image_max_width": "500px",
        "image_max_height": "380px",
        "card_height": 380,
        "text_content": "A sustainable and clean growth of metals mining industry is expected to help contribute towards\n                  a global net-zero economy. Fast technological progress shifts the demand of raw materials across\n                  different commodities.<br>\n                 \n                 <br>Data analytics and processing can play a significant role in debottlenecking and enable cutting\n                 carbon footprints in operational mining processes.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-4 mt-6",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
    {
        "title": "Geothermal",
        "image_file": "DA-for-Geothermal_small.webp",
        "image_max_width": "500px",
        "image_max_height": "380px",
        "card_height": 600,
        "text_content": "Geothermal systems can be the answer to net zero targets in terms of energy, water, and waste. \n                  Electrical and heat energy generated from geothermal systems is renewable, consistent in achieving \n                  baseloads and minimal in producing footprints.<br>\n                 \n                 <br>Data analytics and processing can play a significant role in debottlenecking and enable cutting\n                 carbon footprints in operational mining processes.",
        "text_column_classes": "pl-xl-2 pl-md-16 pt-12 mt-16",
        "button_elevation": '3',
        "button_color": 'primary-lighten-1',
        "button_hover_success": True,
    },
]

print("Starting to seed Brochure data...")

# Clear existing to prevent duplicates
Brochure.objects.all().delete()
print("Cleared existing Brochure records.")

count = 0
for item in brochures_data:
    brochure = Brochure.objects.create(
        title=item["title"],
        image_max_width=item["image_max_width"],
        image_max_height=item["image_max_height"],
        card_height=item["card_height"],
        text_content=item["text_content"],
        text_column_classes=item["text_column_classes"],
        button_elevation=item["button_elevation"],
        button_color=item["button_color"],
        button_hover_success=item["button_hover_success"]
    )
    
    # Process image
    img_path = os.path.join(assets_dir, item["image_file"])
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            brochure.image.save(item["image_file"], File(f), save=True)
            print(f"Saved {item['title']} with image {item['image_file']}")
    else:
        print(f"WARNING: Image not found for {item['title']} - {img_path}")
    
    count += 1

print(f"Successfully seeded {count} brochures!")
