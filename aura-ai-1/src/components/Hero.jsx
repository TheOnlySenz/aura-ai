import React from 'react';
import { motion } from 'framer-motion';

export default function Hero() {
  return (
    <section className="relative flex flex-col items-center justify-center min-h-[80vh] text-center overflow-hidden">
      {/* Animated background gradient */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        className="absolute inset-0 bg-gradient-to-br from-[#232526] via-[#181818] to-[#1a1917] opacity-90 z-0"
        aria-hidden="true"
      />
      {/* Subtle animated shapes */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: [1, 1.05, 1], opacity: [0.15, 0.1, 0.15], rotate: [0, 5, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
        className="absolute -top-24 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-yellow-400 rounded-full blur-3xl z-0"
        aria-hidden="true"
      />
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="relative z-10 text-5xl md:text-6xl font-extrabold text-primary mb-4 drop-shadow-lg"
      >
        Welcome to Aura AI
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.7 }}
        className="relative z-10 text-lg md:text-xl text-gray-200 mb-8 max-w-2xl mx-auto"
      >
        Your intelligent assistant for all your needs.<br className="hidden md:inline" /> Get started with Aura AI today!
      </motion.p>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        className="relative z-10 flex flex-col sm:flex-row gap-4 justify-center items-center mb-8"
      >
        <button
          className="bg-primary text-black font-semibold px-8 py-3 rounded-xl shadow-lg hover:bg-yellow-300 focus:ring-4 focus:ring-yellow-400 transition-all duration-200 text-lg"
          aria-label="Get Started"
          onClick={() => document.getElementById('features')?.scrollIntoView({behavior: 'smooth'})}
        >
          Get Started
        </button>
        <button
          className="bg-transparent border border-primary text-primary font-semibold px-8 py-3 rounded-xl hover:bg-primary/10 focus:ring-4 focus:ring-yellow-400 transition-all duration-200 text-lg"
          aria-label="Learn More"
          onClick={() => document.getElementById('features')?.scrollIntoView({behavior: 'smooth'})}
        >
          Learn More
        </button>
      </motion.div>
      {/* Phone mockup/illustration placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9, duration: 0.8 }}
        className="relative z-10 flex justify-center items-center w-full"
      >
        <motion.img
          src="https://via.placeholder.com/220x440?text=Aura+AI+Preview"
          alt="Aura AI app preview"
          className="w-[220px] h-[440px] rounded-3xl shadow-2xl border-4 border-yellow-400 mx-auto"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.5 }}
        />
      </motion.div>
    </section>
  );
}
