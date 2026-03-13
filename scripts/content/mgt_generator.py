"""MGT level content generator."""

from __future__ import annotations

from typing import Any

from .common import (
    DEFAULT_VERSION,
    build_pack_payload,
    build_question,
    distinct_choices,
    join_sentences,
    load_level_data,
    parse_slot,
    selected,
)


def build_mgt_pack_from_row(
    row: dict[str, str],
    *,
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, Any]:
    slot = parse_slot(row)
    pack_number = int(row["number"])
    data = load_level_data("MGT")
    config = data["topics"][row["topic_group"]]

    title = selected(config, "titles", slot)
    goal = selected(config, "goals", slot)
    first_plan = selected(config, "first_plans", slot)
    problem = selected(config, "problems", slot)
    feedback_group = selected(config, "feedback_groups", slot)
    feedback = selected(config, "feedbacks", slot)
    change_one = selected(config, "change_ones", slot)
    change_two = selected(config, "change_twos", slot)
    change_three = selected(config, "change_threes", slot)
    benefit = selected(config, "benefits", slot)
    improved_result = selected(config, "improved_results", slot)
    principle = selected(config, "principles", slot)
    next_step = selected(config, "next_steps", slot)
    problem_answer = selected(config, "problem_answers", slot)
    q3_prompt = selected(config, "q3_prompts", slot)
    q3_answer = selected(config, "q3_answers", slot)
    vocab_prompt = selected(config, "vocab_prompts", slot)
    vocab_answer = selected(config, "vocab_answers", slot)
    why_answer = selected(config, "why_answers", slot)
    next_answer = selected(config, "next_answers", slot)
    main_answer = selected(config, "main_answers", slot)

    passage = join_sentences(
        [
            f"{goal}.",
            f"At first, {first_plan}, but {problem}.",
            f"{feedback_group} said {feedback}",
            f"After hearing that, the team {change_one} and {change_two}.",
            f"They also {change_three} so {benefit}.",
            f"On the next test day, {improved_result}.",
            f"The team noticed that {principle}.",
            f"Because of that result, {next_step}.",
        ]
    )

    questions = [
        build_question(
            question_id="q1",
            skill="main_idea",
            prompt="What is the passage mainly about?",
            correct=main_answer,
            distractors=distinct_choices(main_answer, data["main_idea_distractors"], 3),
            rationale="The whole passage focuses on improving a system for younger students.",
            seed=pack_number + 1,
        ),
        build_question(
            question_id="q2",
            skill="detail",
            prompt="What problem did students mention about the first plan?",
            correct=problem_answer,
            distractors=distinct_choices(problem_answer, data["problem_pool"], 3),
            rationale="The early part of the passage explains what did not work well.",
            seed=pack_number + 2,
        ),
        build_question(
            question_id="q3",
            skill="detail",
            prompt=q3_prompt,
            correct=q3_answer,
            distractors=distinct_choices(q3_answer, data["change_pool"], 3),
            rationale="The middle of the passage tells what the team added or changed.",
            seed=pack_number + 3,
        ),
        build_question(
            question_id="q4",
            skill="vocab_in_context",
            prompt=vocab_prompt,
            correct=vocab_answer,
            distractors=[
                "A room that is easy to clean",
                "A rule about lunch time",
                "A person who leads the school",
            ],
            rationale="The word meaning comes from the way the passage uses it.",
            seed=pack_number + 4,
        ),
        build_question(
            question_id="q5",
            skill="inference",
            prompt="Why did the new design work better for younger students?",
            correct=why_answer,
            distractors=[
                "It made the room much larger",
                "It reduced the number of students",
                "It removed every sign from the area",
            ],
            rationale="You have to connect the redesign changes with the later results.",
            seed=pack_number + 5,
        ),
        build_question(
            question_id="q6",
            skill="inference",
            prompt="What will the team most likely do next?",
            correct=next_answer,
            distractors=distinct_choices(next_answer, data["next_pool"], 3),
            rationale="The last sentence points to the team's next likely action.",
            seed=pack_number + 6,
        ),
    ]

    return build_pack_payload(
        row=row,
        title=title,
        passage_text=passage,
        questions=questions,
        version=version,
        created_at=created_at,
    )
