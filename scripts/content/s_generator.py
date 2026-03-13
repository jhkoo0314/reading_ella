"""S level content generator."""

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


def build_s_pack_from_row(
    row: dict[str, str],
    *,
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, Any]:
    slot = parse_slot(row)
    pack_number = int(row["number"])
    data = load_level_data("S")
    config = data["topics"][row["topic_group"]]

    title = selected(config, "titles", slot)
    intro = selected(config, "intros", slot)
    actor1 = selected(config, "actor1s", slot)
    method1 = selected(config, "method1s", slot)
    actor2 = selected(config, "actor2s", slot)
    method2 = selected(config, "method2s", slot)
    duration = selected(config, "durations", slot)
    result_subject = selected(config, "result_subjects", slot)
    result_change = selected(config, "result_changes", slot)
    reason = selected(config, "reasons", slot)
    record_sentence = selected(config, "record_sentences", slot)
    record_answer = selected(config, "record_answers", slot)
    observer = selected(config, "observers", slot)
    observer_pronoun = selected(config, "observer_pronouns", slot)
    better_method = selected(config, "better_methods", slot)
    later_sentence = selected(config, "later_sentences", slot)
    lesson = selected(config, "lessons", slot)
    q2_prompt = selected(config, "q2_prompts", slot)
    q2_answer = selected(config, "q2_answers", slot)
    vocab_prompt = selected(config, "vocab_prompts", slot)
    vocab_answer = selected(config, "vocab_answers", slot)
    inference_prompt = selected(config, "inference_prompts", slot)
    inference_answer = selected(config, "inference_answers", slot)
    main_answer = selected(config, "main_answers", slot)

    passage = join_sentences(
        [
            f"{intro} last month.",
            f"{actor1} used {method1}, but {actor2} used {method2}.",
            f"After {duration}, {result_subject} {result_change} because {reason}.",
            record_sentence,
            f"When {observer} saw the difference, {observer_pronoun} changed to {better_method}.",
            later_sentence,
            "The students talked about the test before choosing a better method.",
            f"The group learned that {lesson}.",
        ]
    )

    questions = [
        build_question(
            question_id="q1",
            skill="main_idea",
            prompt="What is the passage mostly about?",
            correct=main_answer,
            distractors=distinct_choices(main_answer, data["main_idea_distractors"], 3),
            rationale="The whole passage follows one test and what the group learned from it.",
            seed=pack_number + 1,
        ),
        build_question(
            question_id="q2",
            skill="detail",
            prompt=q2_prompt,
            correct=q2_answer,
            distractors=distinct_choices(
                q2_answer,
                [
                    "A long paper list",
                    "A toy basket",
                    "A paint brush",
                    "A music book",
                    "A wall poster",
                ],
                3,
            ),
            rationale="The second sentence directly tells which tool or place was used.",
            seed=pack_number + 2,
        ),
        build_question(
            question_id="q3",
            skill="detail",
            prompt="What did the group check or write down?",
            correct=record_answer,
            distractors=distinct_choices(record_answer, data["record_pool"], 3),
            rationale="The fourth sentence explains what the group checked or recorded.",
            seed=pack_number + 3,
        ),
        build_question(
            question_id="q4",
            skill="vocab_in_context",
            prompt="What does difference mean in the fifth sentence?",
            correct="The way two things are not the same",
            distractors=[
                "A list of class rules",
                "A place to store tools",
                "A loud sound in a room",
            ],
            rationale="Difference means the two results did not match each other.",
            seed=pack_number + 4,
        ),
        build_question(
            question_id="q5",
            skill="vocab_in_context",
            prompt=vocab_prompt,
            correct=vocab_answer,
            distractors=[
                "A color on the wall",
                "A person who visits a club",
                "A kind of snack",
            ],
            rationale="The word meaning comes from how it is used in the passage.",
            seed=pack_number + 5,
        ),
        build_question(
            question_id="q6",
            skill="inference",
            prompt=inference_prompt,
            correct=inference_answer,
            distractors=[
                "The teacher told the student to stop working",
                "The group wanted to decorate the room more",
                "The first tool was missing from the class",
            ],
            rationale="The student changed after seeing which method worked better.",
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
