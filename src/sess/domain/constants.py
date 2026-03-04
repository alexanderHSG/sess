"""Shared constants for the application domain."""

from __future__ import annotations

CATEGORY_CHOICES: tuple[str, ...] = (
    "Research",
    "Technology",
    "Business",
    "Design",
    "Storyboards",
    "Science",
    "How-to & DIY",
    "Education",
    "Programming",
    "Marketing & SEO",
    "Other",
)

AUTHOR_CHOICES: tuple[str, ...] = (
    "speaker_addyosmani",
    "speaker_ajstarks",
    "speaker_aleyda",
    "speaker_ange",
    "speaker_brainpadpr",
    "speaker_cmaneu",
    "speaker_cygames",
    "speaker_dabeaz",
    "speaker_daipresents",
    "speaker_devnetnoord",
    "speaker_dfm",
    "speaker_doradora09",
    "speaker_dotnetday",
    "speaker_dunglas",
    "speaker_eddie",
    "speaker_eileencodes",
    "speaker_elasticsearch",
    "speaker_ericstoller",
    "speaker_eueung",
    "speaker_fixstars",
    "speaker_fmunz",
    "speaker_fr0gger",
    "speaker_freee",
    "speaker_gunnarmorling",
    "speaker_hatena",
    "speaker_heyitsmohit",
    "speaker_hpgrahsl",
    "speaker_inamiy",
    "speaker_ivargrimstad",
    "speaker_iwashi86",
    "speaker_jamf",
    "speaker_jennybc",
    "speaker_jhellerstein",
    "speaker_joergneumann",
    "speaker_johtani",
    "speaker_jollyjoester",
    "speaker_kazupon",
    "speaker_kishida",
    "speaker_konakalab",
    "speaker_konifar",
    "speaker_kurochan",
    "speaker_leastprivilege",
    "speaker_lemiorhan",
    "speaker_leriomaggio",
    "speaker_letsconnect",
    "speaker_libshare",
    "speaker_linedevth",
    "speaker_luxas",
    "speaker_mamohacy",
    "speaker_marcduiker",
    "speaker_martinlippert",
    "speaker_matleenalaakso",
    "speaker_medley",
    "speaker_mikecohn",
    "speaker_mitsuhiko",
    "speaker_miyakemito",
    "speaker_mottox2",
    "speaker_mploed",
    "speaker_nihonbuson",
    "speaker_nileshgule",
    "speaker_no24oka",
    "speaker_ocise",
    "speaker_off2class",
    "speaker_olivergierke",
    "speaker_opelab",
    "speaker_other",
    "speaker_palkan",
    "speaker_paperswelove",
    "speaker_pauldix",
    "speaker_pichuang",
    "speaker_pixely",
    "speaker_prof18",
    "speaker_publicservicelab",
    "speaker_pyama86",
    "speaker_pycon2015",
    "speaker_pycon2016",
    "speaker_quasilyte",
    "speaker_rachelhch",
    "speaker_ramalho",
    "speaker_redhatlivestreaming",
    "speaker_reverentgeek",
    "speaker_rmcelreath",
    "speaker_rnakamuramartiny",
    "speaker_rtechkouhou",
    "speaker_sansanbuildersbox",
    "speaker_senryakuka",
    "speaker_shah",
    "speaker_shlominoach",
    "speaker_soudai",
    "speaker_tagtag",
    "speaker_takaking22",
    "speaker_takashitanaka",
    "speaker_tammielis",
    "speaker_tenforward",
    "speaker_thockin",
    "speaker_thomasvitale",
    "speaker_toshiseisaku",
    "speaker_tosseto",
    "speaker_uzulla",
    "speaker_welcometomusic",
    "speaker_wescale",
    "speaker_yasuoyasuo",
    "speaker_ymatsuwitter",
    "speaker_yohhatu",
    "speaker_yoshiakiyamasaki",
    "speaker_ytaka23",
    "speaker_ythecombinator",
    "speaker_yuyumoyuyu",
    "speaker_zoomquiet",
)

FACTUALITY_PARSE_INSTRUCTION = (
    "The provided document is a presentation slide deck. "
    "It could contain tables, images, diagrams and text. "
    "Extract the text content from the document. "
    "Output any math equation in LATEX markdown (between $$). "
    "For diagrams and images additionally describe the visual content. "
    "Be as concise as possible. Multiple lives are at stake. You must get this right."
)

SLIDE_FEEDBACK_PROMPT = "\n".join(
    (
        "provide a SHORT and concise prescriptive feedback on the slide. "
        "Avoid euphemistic feedback, be critical.",
        "Use the following question to guide your feedback, NOT all checkpoints "
        "at once need be applicable to this slide,",
        "consider wisely which one to recommend specifically. "
        "Do NOT just repeat the checkpoint descriptions.",
        "Additionally, if a checkpoint is applicable describe WHERE and HOW "
        "in the slide the checkpoints should implemented:",
        "1. Insert a pictogram. Pictogram insertion can intuitively convey the slide content.",
        "2. Add a subheading. Subheading addition makes the audiences "
        "convenient to find information.",
        "3. Emphasize words. Emphasizing important words enhances a part "
        "of a text to make it noticeable.",
        "4. Emphasize areas. Emphasizing important areas of the slides helps focus attention.",
        "5. Add T1 and T2. Slide title (T1) and slide messages (T2) help the audiences "
        "more easily understand the main content of the exposition.",
        "6. Use the grid structure. A grid structure helps organize target and comparison items "
        "in rows and columns, creating a table-like format.",
        "7. Itemize the text. Text itemization is good in terms of readability and organization.",
        "8. Add a comment. Comments aid in audiences' understanding.",
        "9. Correct flow. Left-to-right top-to-bottom flow mimics human scanning methods.",
        "10. MECE. Mutually exclusive and collectively exhaustive (MECE) objects should be aligned "
        "without omissions and duplication to make the slides convincing.",
        "11. Consistent formatting. Look for and point out inconsistencies.",
        "12. Add an Action Title. Action titles make the audiences understand "
        "the key take-away easy and fast.",
        "13. Citation style. Scientific sources are cited consistently via "
        "the same citation style.",
    )
)
