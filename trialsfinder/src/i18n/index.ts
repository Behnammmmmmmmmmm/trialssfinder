import { format } from 'date-fns';
import { enUS, es, fr, de, ar, he } from 'date-fns/locale';
import { useTranslation as useI18nTranslation } from 'react-i18next';

const locales = { en: enUS, es, fr, de, ar, he };

export const useTranslation = () => {
  const { t, i18n } = useI18nTranslation();
  
  const formatDate = (date: Date | string, formatStr = 'PP') => {
    const locale = locales[i18n.language as keyof typeof locales] || enUS;
    return format(new Date(date), formatStr, { locale });
  };
  
  const formatCurrency = (amount: number, currency = 'USD') => {
    return new Intl.NumberFormat(i18n.language, {
      style: 'currency',
      currency,
    }).format(amount);
  };
  
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat(i18n.language).format(num);
  };
  
  return {
    t,
    i18n,
    formatDate,
    formatCurrency,
    formatNumber,
    isRTL: ['ar', 'he'].includes(i18n.language),
  };
};

export { default as i18n } from './config';