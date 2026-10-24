"""Mathematics Curriculum Definition with Prerequisite Graph.

Covers 10 core mathematical domains for learners aged 8-14:
1. Addition & Subtraction
2. Multiplication & Division
3. Fractions & Equivalent Fractions
4. Comparing & Ordering Fractions
5. Fraction Addition & Subtraction
6. Decimals & Percentages
7. Ratios & Proportions
8. Basic Algebra
9. Geometry & Measurement
10. Number Patterns & Logical Reasoning
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ConceptDefinition:
    id: str
    title: str
    topic_id: str
    description: str
    learning_objective: str
    difficulty_levels: List[int]
    prerequisites: List[str] = field(default_factory=list)
    common_misconceptions: Dict[str, str] = field(default_factory=dict)


@dataclass
class TopicDefinition:
    id: str
    title: str
    description: str
    order: int
    concepts: List[ConceptDefinition]


CURRICULUM: Dict[str, TopicDefinition] = {
    "add_sub": TopicDefinition(
        id="add_sub",
        title="Addition & Subtraction",
        description="Core arithmetic operations with whole numbers and integers",
        order=1,
        concepts=[
            ConceptDefinition(
                id="add_single_digit",
                title="Single-Digit Addition",
                topic_id="add_sub",
                description="Fluency with basic addition facts up to 20",
                learning_objective="Recall single-digit addition sums with speed and precision",
                difficulty_levels=[1, 2],
                prerequisites=[],
                common_misconceptions={"count_all": "Counting on fingers from 1 instead of counting on"},
            ),
            ConceptDefinition(
                id="sub_single_digit",
                title="Single-Digit Subtraction",
                topic_id="add_sub",
                description="Fluency with basic subtraction facts within 20",
                learning_objective="Subtract single-digit numbers accurately",
                difficulty_levels=[1, 2],
                prerequisites=["add_single_digit"],
                common_misconceptions={"smaller_from_larger": "Subtracting smaller digit from larger regardless of order"},
            ),
            ConceptDefinition(
                id="add_sub_multi_digit",
                title="Multi-Digit Addition & Subtraction",
                topic_id="add_sub",
                description="Carrying and borrowing across 2-digit and 3-digit numbers",
                learning_objective="Perform multi-digit addition and regrouping in subtraction",
                difficulty_levels=[2, 3, 4],
                prerequisites=["sub_single_digit"],
                common_misconceptions={"forget_borrow": "Omitting the borrowed ten from the adjacent column"},
            ),
            ConceptDefinition(
                id="integers_add_sub",
                title="Negative Numbers Addition & Subtraction",
                topic_id="add_sub",
                description="Working with positive and negative integers on a number line",
                learning_objective="Add and subtract directed numbers correctly",
                difficulty_levels=[3, 4, 5],
                prerequisites=["add_sub_multi_digit"],
                common_misconceptions={"double_negative": "Confusing subtract-a-negative with adding a negative"},
            ),
        ],
    ),
    "mul_div": TopicDefinition(
        id="mul_div",
        title="Multiplication & Division",
        description="Repeated addition, times tables, long division, and factor concepts",
        order=2,
        concepts=[
            ConceptDefinition(
                id="multiplication_facts",
                title="Times Tables (2 to 12)",
                topic_id="mul_div",
                description="Recall of multiplication tables",
                learning_objective="Rapidly solve basic multiplication facts",
                difficulty_levels=[1, 2, 3],
                prerequisites=["add_single_digit"],
                common_misconceptions={"additive_jump": "Adding factors rather than multiplying"},
            ),
            ConceptDefinition(
                id="basic_division",
                title="Equal Sharing & Division Facts",
                topic_id="mul_div",
                description="Inverse relationship of multiplication and division",
                learning_objective="Calculate single and double-digit division quotients",
                difficulty_levels=[2, 3],
                prerequisites=["multiplication_facts"],
                common_misconceptions={"remainder_ignored": "Ignoring remainders or confusing quotient with divisor"},
            ),
            ConceptDefinition(
                id="multi_digit_multiplication",
                title="Multi-Digit Multiplication",
                topic_id="mul_div",
                description="Multiplying 2-digit numbers by 1-digit and 2-digit factors",
                learning_objective="Multiply multi-digit numbers using place value",
                difficulty_levels=[3, 4, 5],
                prerequisites=["multiplication_facts"],
                common_misconceptions={"place_value_shift": "Forgetting the zero placeholder when multiplying tens"},
            ),
            ConceptDefinition(
                id="order_of_operations",
                title="Order of Operations (PEMDAS)",
                topic_id="mul_div",
                description="Evaluating expressions respecting parenthesis and precedence",
                learning_objective="Apply multiplication before addition in combined expressions",
                difficulty_levels=[3, 4, 5],
                prerequisites=["basic_division", "add_sub_multi_digit"],
                common_misconceptions={"left_to_right_strict": "Evaluating left-to-right ignoring operator precedence"},
            ),
        ],
    ),
    "fractions_intro": TopicDefinition(
        id="fractions_intro",
        title="Fractions & Equivalent Fractions",
        description="Parts of a whole, numerators, denominators, and equivalent fractions",
        order=3,
        concepts=[
            ConceptDefinition(
                id="fraction_concepts",
                title="Parts of a Whole & Visual Models",
                topic_id="fractions_intro",
                description="Understanding numerator as count and denominator as equal parts",
                learning_objective="Identify proper and improper fractions from descriptions and models",
                difficulty_levels=[1, 2],
                prerequisites=["basic_division"],
                common_misconceptions={"inverted_parts": "Swapping numerator and denominator"},
            ),
            ConceptDefinition(
                id="equivalent_fractions",
                title="Equivalent Fractions & Simplification",
                topic_id="fractions_intro",
                description="Scaling numerators and denominators by common factors",
                learning_objective="Find equivalent fractions and simplify to lowest terms",
                difficulty_levels=[2, 3, 4],
                prerequisites=["fraction_concepts", "multiplication_facts"],
                common_misconceptions={"additive_scaling": "Adding a constant to both numerator and denominator instead of multiplying"},
            ),
        ],
    ),
    "fractions_compare": TopicDefinition(
        id="fractions_compare",
        title="Comparing & Ordering Fractions",
        description="Comparing fractions with like and unlike denominators",
        order=4,
        concepts=[
            ConceptDefinition(
                id="compare_like_denominators",
                title="Comparing Like Denominators",
                topic_id="fractions_compare",
                description="Comparing fractions sharing the same denominator",
                learning_objective="Order and compare fractions having identical denominators",
                difficulty_levels=[1, 2],
                prerequisites=["fraction_concepts"],
                common_misconceptions={"larger_denom_is_more": "Believing larger denominator means larger quantity"},
            ),
            ConceptDefinition(
                id="compare_unlike_denominators",
                title="Comparing Unlike Denominators",
                topic_id="fractions_compare",
                description="Cross-multiplication or common denominators to compare fractions",
                learning_objective="Determine which of two unlike fractions is greater or if they are equal",
                difficulty_levels=[3, 4, 5],
                prerequisites=["compare_like_denominators", "equivalent_fractions"],
                common_misconceptions={"numerator_dominant": "Comparing numerators alone while ignoring denominators"},
            ),
        ],
    ),
    "fractions_ops": TopicDefinition(
        id="fractions_ops",
        title="Fraction Addition & Subtraction",
        description="Combining and partitioning fractions with like and unlike denominators",
        order=5,
        concepts=[
            ConceptDefinition(
                id="add_sub_like_fractions",
                title="Adding & Subtracting Like Fractions",
                topic_id="fractions_ops",
                description="Adding numerators while retaining the common denominator",
                learning_objective="Compute sums and differences of fractions with identical denominators",
                difficulty_levels=[2, 3],
                prerequisites=["compare_like_denominators"],
                common_misconceptions={"add_denominators": "Adding the denominators together (e.g. 1/4 + 2/4 = 3/8)"},
            ),
            ConceptDefinition(
                id="add_sub_unlike_fractions",
                title="Adding & Subtracting Unlike Fractions",
                topic_id="fractions_ops",
                description="Finding common denominators before combining",
                learning_objective="Convert unlike fractions to a common denominator and find the sum or difference",
                difficulty_levels=[3, 4, 5],
                prerequisites=["add_sub_like_fractions", "equivalent_fractions"],
                common_misconceptions={"add_denominators_direct": "Adding numerators and adding denominators directly without common base"},
            ),
        ],
    ),
    "decimals_percents": TopicDefinition(
        id="decimals_percents",
        title="Decimals & Percentages",
        description="Tenths, hundredths, place value, and percentage conversion",
        order=6,
        concepts=[
            ConceptDefinition(
                id="decimal_place_value",
                title="Decimal Place Value & Comparison",
                topic_id="decimals_percents",
                description="Understanding tenths, hundredths, and comparing decimals",
                learning_objective="Compare and order decimal values accurately",
                difficulty_levels=[2, 3],
                prerequisites=["equivalent_fractions"],
                common_misconceptions={"longer_is_larger": "Assuming 0.125 is larger than 0.5 because 125 > 5"},
            ),
            ConceptDefinition(
                id="decimal_arithmetic",
                title="Decimal Addition & Subtraction",
                topic_id="decimals_percents",
                description="Aligning decimal points for addition and subtraction",
                learning_objective="Add and subtract decimal values to two decimal places",
                difficulty_levels=[2, 3, 4],
                prerequisites=["decimal_place_value", "add_sub_multi_digit"],
                common_misconceptions={"right_align_decimals": "Right-aligning numbers instead of aligning decimal points"},
            ),
            ConceptDefinition(
                id="percent_basics",
                title="Percentages as Hundredths",
                topic_id="decimals_percents",
                description="Converting between fractions, decimals, and percentages",
                learning_objective="Calculate 10%, 25%, 50%, and convert percentages to decimals/fractions",
                difficulty_levels=[3, 4, 5],
                prerequisites=["decimal_place_value"],
                common_misconceptions={"percent_as_integer": "Treating 25% as 25 rather than 25/100 or 0.25"},
            ),
        ],
    ),
    "ratios_proportions": TopicDefinition(
        id="ratios_proportions",
        title="Ratios & Proportions",
        description="Part-to-part, part-to-whole comparisons, and proportional scaling",
        order=7,
        concepts=[
            ConceptDefinition(
                id="ratio_representation",
                title="Expressing & Simplifying Ratios",
                topic_id="ratios_proportions",
                description="Writing ratios in simplest form (a:b)",
                learning_objective="Simplify ratios and identify equivalent ratios",
                difficulty_levels=[2, 3, 4],
                prerequisites=["multiplication_facts", "equivalent_fractions"],
                common_misconceptions={"part_whole_confusion": "Confusing part:part ratio with part:total fraction"},
            ),
            ConceptDefinition(
                id="unitary_method",
                title="Unitary Method & Proportional Reasoning",
                topic_id="ratios_proportions",
                description="Finding the value of one unit to solve scaling word problems",
                learning_objective="Use proportional thinking to scale quantities up and down",
                difficulty_levels=[3, 4, 5],
                prerequisites=["ratio_representation", "basic_division"],
                common_misconceptions={"additive_scaling_ratio": "Adding the same amount to both terms of a ratio"},
            ),
        ],
    ),
    "basic_algebra": TopicDefinition(
        id="basic_algebra",
        title="Basic Algebra",
        description="Variables, balancing equations, and one-step/two-step linear equations",
        order=8,
        concepts=[
            ConceptDefinition(
                id="missing_number_equations",
                title="Missing Number Problems & Balancing",
                topic_id="basic_algebra",
                description="Finding the unknown value in box/variable arithmetic (e.g. x + 7 = 15)",
                learning_objective="Solve one-step addition and subtraction equations",
                difficulty_levels=[2, 3],
                prerequisites=["add_sub_multi_digit"],
                common_misconceptions={"equals_means_calculate": "Viewing the equals sign as an operation rather than an equivalence balance"},
            ),
            ConceptDefinition(
                id="linear_equations_one_step",
                title="One-Step Multiplication & Division Equations",
                topic_id="basic_algebra",
                description="Solving equations like 3x = 21 or x/4 = 5",
                learning_objective="Isolate variables using inverse operations",
                difficulty_levels=[3, 4],
                prerequisites=["missing_number_equations", "basic_division"],
                common_misconceptions={"wrong_inverse": "Multiplying instead of dividing when undoing a coefficient"},
            ),
            ConceptDefinition(
                id="linear_equations_two_step",
                title="Two-Step Linear Equations",
                topic_id="basic_algebra",
                description="Solving 2x + 5 = 17 using standard algebraic sequence",
                learning_objective="Solve two-step linear equations systematically",
                difficulty_levels=[4, 5],
                prerequisites=["linear_equations_one_step", "order_of_operations"],
                common_misconceptions={"undo_order_error": "Dividing before subtracting the constant term"},
            ),
        ],
    ),
    "geometry_measurement": TopicDefinition(
        id="geometry_measurement",
        title="Geometry & Measurement",
        description="Perimeter, area, angles, and unit conversions",
        order=9,
        concepts=[
            ConceptDefinition(
                id="perimeter_calculation",
                title="Perimeter of 2D Shapes",
                topic_id="geometry_measurement",
                description="Calculating the boundary length of rectangles, triangles, and polygons",
                learning_objective="Sum side lengths to determine perimeter",
                difficulty_levels=[2, 3],
                prerequisites=["add_sub_multi_digit"],
                common_misconceptions={"confuse_perimeter_area": "Multiplying sides instead of adding when calculating perimeter"},
            ),
            ConceptDefinition(
                id="area_rectangles",
                title="Area of Rectangles & Triangles",
                topic_id="geometry_measurement",
                description="Using length x width and (base x height) / 2",
                learning_objective="Calculate area of 2D shapes with correct square units",
                difficulty_levels=[3, 4, 5],
                prerequisites=["perimeter_calculation", "multiplication_facts"],
                common_misconceptions={"confuse_area_perimeter": "Adding sides instead of multiplying when finding area"},
            ),
            ConceptDefinition(
                id="angle_properties",
                title="Angles on a Straight Line & Triangles",
                topic_id="geometry_measurement",
                description="Sum of angles in a triangle (180°) and on a line (180°)",
                learning_objective="Find unknown interior angles in triangles and straight lines",
                difficulty_levels=[3, 4, 5],
                prerequisites=["add_sub_multi_digit"],
                common_misconceptions={"angle_sum_confusion": "Confusing 180° triangle sum with 360° quadrilateral sum"},
            ),
        ],
    ),
    "patterns_logic": TopicDefinition(
        id="patterns_logic",
        title="Number Patterns & Logical Reasoning",
        description="Arithmetic sequences, geometric patterns, and deductive logic",
        order=10,
        concepts=[
            ConceptDefinition(
                id="arithmetic_sequences",
                title="Arithmetic Number Sequences",
                topic_id="patterns_logic",
                description="Identifying constant differences and finding next terms",
                learning_objective="Detect rule of a sequence (+3, -4) and determine next term",
                difficulty_levels=[1, 2, 3],
                prerequisites=["add_sub_multi_digit"],
                common_misconceptions={"inconsistent_step": "Only checking difference between first two terms"},
            ),
            ConceptDefinition(
                id="geometric_sequences",
                title="Multiplicative Sequences",
                topic_id="patterns_logic",
                description="Doubling, halving, and constant factor progressions",
                learning_objective="Detect multiplicative patterns (e.g. 3, 6, 12, 24)",
                difficulty_levels=[3, 4, 5],
                prerequisites=["arithmetic_sequences", "multiplication_facts"],
                common_misconceptions={"additive_assumption": "Trying to apply an arithmetic difference to an exponential pattern"},
            ),
        ],
    ),
}


def get_all_concepts() -> List[ConceptDefinition]:
    """Return flat list of all concept definitions."""
    concepts: List[ConceptDefinition] = []
    for topic in CURRICULUM.values():
        concepts.extend(topic.concepts)
    return concepts


def get_concept_by_id(concept_id: str) -> Optional[ConceptDefinition]:
    """Look up a concept by its unique ID."""
    for topic in CURRICULUM.values():
        for c in topic.concepts:
            if c.id == concept_id:
                return c
    return None


def get_topic_by_id(topic_id: str) -> Optional[TopicDefinition]:
    """Look up a topic by its ID."""
    return CURRICULUM.get(topic_id)
