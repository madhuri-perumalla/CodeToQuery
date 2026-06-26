import React from 'react';
import { Box, Typography, Link, useTheme, useMediaQuery, Divider } from '@mui/material';

interface FooterProps {
  showFullFooter?: boolean;
}

export const Footer: React.FC<FooterProps> = ({ showFullFooter = true }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  if (isMobile && !showFullFooter) {
    return null;
  }

  return (
    <Box
      component="footer"
      sx={{
        bgcolor: '#0F1115',
        borderTop: '1px solid #242830',
        py: isMobile ? 2 : 3,
        px: isMobile ? 2 : 3,
        mt: 'auto',
      }}
    >
      {!isTablet && showFullFooter ? (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 3,
            mb: 3,
          }}
        >
          {/* Product Column */}
          <Box>
            <Typography
              variant="subtitle2"
              sx={{
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 2,
                fontSize: '0.875rem',
              }}
            >
              Product
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Features
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Pricing
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Documentation
              </Link>
            </Box>
          </Box>

          {/* Resources Column */}
          <Box>
            <Typography
              variant="subtitle2"
              sx={{
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 2,
                fontSize: '0.875rem',
              }}
            >
              Resources
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Blog
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Tutorials
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                API Reference
              </Link>
            </Box>
          </Box>

          {/* Company Column */}
          <Box>
            <Typography
              variant="subtitle2"
              sx={{
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 2,
                fontSize: '0.875rem',
              }}
            >
              Company
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                About
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Careers
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Contact
              </Link>
            </Box>
          </Box>

          {/* Legal Column */}
          <Box>
            <Typography
              variant="subtitle2"
              sx={{
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 2,
                fontSize: '0.875rem',
              }}
            >
              Legal
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Privacy Policy
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Terms of Service
              </Link>
              <Link
                href="#"
                sx={{
                  color: '#B0B3B8',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#3F51B5',
                    textDecoration: 'underline',
                  },
                }}
              >
                Security
              </Link>
            </Box>
          </Box>
        </Box>
      ) : null}

      <Divider sx={{ borderColor: '#242830', mb: 2 }} />

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
          © 2024 CodeToQuery. All rights reserved.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
            Version 1.0.0
          </Typography>
          <Link
            href="#"
            sx={{
              color: '#3F51B5',
              fontSize: '0.75rem',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            }}
          >
            Help Center
          </Link>
        </Box>
      </Box>
    </Box>
  );
};
