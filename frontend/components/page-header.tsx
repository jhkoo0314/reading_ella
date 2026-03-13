"use client";

import { motion } from "framer-motion";

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
};

export function PageHeader({ eyebrow, title, description, actions }: PageHeaderProps) {
  return (
    <header className="page-header page-header--playful">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="page-header__content-box"
      >
        {eyebrow ? <p className="page-header__eyebrow">✨ {eyebrow}</p> : null}
        <h1 className="page-header__title">
          {title} <span className="title-emoji">📚</span>
        </h1>
        {description ? <p className="page-header__description">{description}</p> : null}
      </motion.div>
      {actions ? (
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {actions}
        </motion.div>
      ) : null}
    </header>
  );
}
