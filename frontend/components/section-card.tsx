"use client";

import { motion } from "framer-motion";

type SectionCardProps = {
  title?: string;
  description?: string;
  children: React.ReactNode;
};


export function SectionCard({ title, description, children }: SectionCardProps) {
  return (
    <motion.section
      className="section-card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {title || description ? (
        <div className="section-card__header">
          {title ? <h2 className="section-card__title">{title}</h2> : null}
          {description ? <p className="section-card__description">{description}</p> : null}
        </div>
      ) : null}
      <div className="section-card__body">{children}</div>
    </motion.section>
  );
}
