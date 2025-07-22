export const useTranslation = () => {
  return {
    t: (key: string) => key,
    i18n: {
      language: 'en',
      changeLanguage: jest.fn(),
      use: jest.fn(),
      init: jest.fn(),
    },
    formatDate: jest.fn((date) => date.toString()),
  };
};