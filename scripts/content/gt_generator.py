"""GT level content generator."""

from __future__ import annotations

from typing import Any

from .common import (
    DEFAULT_VERSION,
    build_pack_payload,
    build_question,
    distinct_choices,
    format_time_phrase,
    join_sentences,
    load_common_data,
    load_level_data,
    parse_slot,
    pick,
    selected,
)


def build_gt_pack_from_row(
    row: dict[str, str],
    *,
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, Any]:
    slot = parse_slot(row)
    pack_number = int(row["number"])
    data = load_level_data("GT")
    common_data = load_common_data()
    config = data["topics"][row["topic_group"]]

    title = selected(config, "titles", slot)
    item = selected(config, "items", slot, 1)
    location = selected(config, "locations", slot, 2)
    time = selected(config, "times", slot)
    before = selected(config, "befores", slot, 1)
    action = selected(config, "actions", slot, 2)
    supplies_text = selected(config, "supplies_text", slot)
    supply_label = selected(config, "supply_labels", slot)
    guide = selected(config, "guides", slot, 1)
    task = selected(config, "tasks", slot, 2)
    compare_object = selected(config, "objects", slot)
    benefit = selected(config, "benefits", slot, 1)
    actor = pick(common_data["names"], slot, 2)
    time_phrase = format_time_phrase(time)
    time_choice = time_phrase[:1].upper() + time_phrase[1:]

    passage = join_sentences(
        [
            f"Our group keeps a {item} {location}.",
            f"{time_choice}, {actor} {action} before {before}.",
            f"The {item} has {supplies_text} for the day's job.",
            f"{guide} asks us to {task}.",
            f"Sometimes we compare today's {compare_object} with yesterday's {compare_object} and notice one small change.",
            f"We like the {item} because it helps us {benefit}.",
        ]
    )

    questions = [
        build_question(
            question_id="q1",
            skill="main_idea",
            prompt="What is this passage mostly about?",
            correct=f"Using the {item}",
            distractors=distinct_choices(f"Using the {item}", data["main_idea_distractors"], 3),
            rationale=f"The whole passage explains how the {item} is used.",
            seed=pack_number + 1,
        ),
        build_question(
            question_id="q2",
            skill="detail",
            prompt=f"Where is the {item}?",
            correct=location,
            distractors=distinct_choices(location, data["location_pool"], 3),
            rationale=f"The first sentence says the {item} is {location}.",
            seed=pack_number + 2,
        ),
        build_question(
            question_id="q3",
            skill="detail",
            prompt=f"When does {actor} use the {item}?",
            correct=time_choice,
            distractors=distinct_choices(time_choice, data["time_pool"], 3),
            rationale=f"The second sentence says {actor} uses it {time_phrase}.",
            seed=pack_number + 3,
        ),
        build_question(
            question_id="q4",
            skill="detail",
            prompt=f"What does the {item} have?",
            correct=supply_label,
            distractors=distinct_choices(supply_label, data["supply_pool"], 3),
            rationale=f"The third sentence says the {item} has {supply_label.lower()}.",
            seed=pack_number + 4,
        ),
        build_question(
            question_id="q5",
            skill="vocab_in_context",
            prompt="What does compare mean in the fifth sentence?",
            correct="Look at two things together",
            distractors=[
                "Start a noisy game",
                "Hide something quickly",
                "Finish all the work",
            ],
            rationale="Compare means to look at two things and think about them together.",
            seed=pack_number + 5,
        ),
        build_question(
            question_id="q6",
            skill="vocab_in_context",
            prompt="What does notice mean in the fifth sentence?",
            correct="See something important",
            distractors=[
                "Make a loud sound",
                "Carry a heavy box",
                "Draw a new picture",
            ],
            rationale="Notice means to see and pay attention to something.",
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
