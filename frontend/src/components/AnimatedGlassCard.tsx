import { motion } from 'framer-motion'
import { PropsWithChildren } from 'react'

export default function AnimatedGlassCard({
  children,
  className = ''
}: PropsWithChildren<{ className?: string }>) {
  return (
    <motion.div
      className={`glass rounded-2xl ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      whileHover={{ scale: 1.005 }}
    >
      {children}
    </motion.div>
  )
}

