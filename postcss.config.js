const purgecss = require('@fullhuman/postcss-purgecss')

module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    purgecss({
      content: [
        './StudentConnect/templates/search.html', // Actual template file names
        ],
      defaultExtractor: (content) => content.match(/[\w-/:]+(?<!:)/g) || [], // Extracts Tailwind classes
    })
  ]
}