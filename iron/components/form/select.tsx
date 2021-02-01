import { FormControl, InputLabel, MenuItem, Select } from "@material-ui/core";

type FormSelectOption = {
  value: string;
  text: string;
};

type FormSelect<T> = {
  data: FormSelectOption[];
  onChange: (e: any) => void;
  name: string;
  inField: string;
  nameField: string;
  label: string;
};

function FormSelect({ data, onChange, name, label }) {
  return (
    <FormControl fullWidth>
      <InputLabel htmlFor={`vertex-{name}`}>{label}</InputLabel>
      <Select id={`vertex-{name}`} onChange={onChange} displayEmpty>
        <MenuItem value="">
          <em>None</em>
        </MenuItem>
        {data.map(({ value, text }) => (
          <MenuItem value={value}>{text}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export default FormSelect;
