import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';

export const Button: React.FC<MuiButtonProps> = ({ children, ...props }) => {
  return (
    <MuiButton {...props} variant="contained">
      {children}
    </MuiButton>
  );
};
